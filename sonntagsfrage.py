import database
from requests_html import HTMLSession
from datetime import date, datetime, timedelta
import sys
import matplotlib.pyplot as plt
import numpy as np
import matplotlib


def get_new_values():
    ret_array = []
    session = HTMLSession()
    r = session.get('https://www.wahlrecht.de/umfragen/')
    institute = ['Allensbach', 'Kantar', 'Forsa', 'Politbarometer', 'GMS', 'dimap', 'insa', 'yougov']
    datum = r.html.find('#datum', first=True).text.split('\n')[1:-1]
    cdu = r.html.find('#cdu', first=True).text.split('\n')[1:-1]
    spd = r.html.find('#spd', first=True).text.split('\n')[1:-1]
    gru = r.html.find('#gru', first=True).text.split('\n')[1:-1]
    fdp = r.html.find('#fdp', first=True).text.split('\n')[1:-1]
    lin = r.html.find('#lin', first=True).text.split('\n')[1:-1]
    afd = r.html.find('#afd', first=True).text.split('\n')[1:-1]
    son = r.html.find('#son', first=True).text.split('\n')[1:-1]
    tablein = [institute, datum, cdu, spd, gru, fdp, lin, afd, son]
    for i in range(8):
        temparray = []
        for j in range(9):
            temparray.append(tablein[j][i])
        ret_array.append(temparray)
    return ret_array


def main():
    chgbool = False
    dab = database.DataBase()
    db = dab.db
    con = dab.con
    if len(sys.argv) != 2:
        print(
            "Syntax: python.exe sonntagsfrage.py -g | -d\n entweder -g: Neue Daten holen\n oder -d: Zeichne Graphen")
        sys.exit()
    arg = sys.argv[1]
    if not (arg == '-d' or arg == "-g"):
        print(
            "Syntax: python.exe sonntagsfrage.py -g | -d\n entweder -g: Neue Daten holen\n oder -d: Zeichne Graphen")
        sys.exit()
    if arg == "-g":
        table = get_new_values()
        fields = "institut,datum,cdu,spd,gru,fdp,lin,afd,son"
        sqlinfos = []
        today = date.today()
        for i in table:
            sqlin = ""
            for j in i:
                stra = "'" + str(j).replace(',', '.') + "', "
                numeric_filter = filter(str.isdigit, stra)
                stra = "".join(numeric_filter)
                sqlin += stra
            sqlinfos.append(sqlin.lstrip().rstrip().rstrip(',').replace(' %', ''))
        for i in range(len(sqlinfos)):
            sql = "CREATE TABLE if not exists " + table[i][
                0] + "(datum DATE PRIMARY KEY, cdu VARCHAR(64), spd VARCHAR(64), gru VARCHAR(64), fdp VARCHAR(64), lin VARCHAR(64), afd VARCHAR(64), son VARCHAR(64));"
            db.execute(sql)
            con.commit()
            sql = "SELECT institut FROM sonntagsfrage WHERE institut ='" + table[i][0] + "';"
            ergu = db.execute(sql).fetchone()
            lengu = len(ergu)
            ins = table[i][0]
            sql = "SELECT datum FROM sonntagsfrage WHERE institut='update';"
            erg = db.execute(sql).fetchone()
            leng = len(erg)
            if leng == 0:
                datedt = today - timedelta(days=1)
            else:
                year = erg[0].split('-')[0]
                month = erg[0].split('-')[1]
                day = erg[0].split('-')[2]
                datedt = datetime(int(year), int(month), int(day))
            if today > datedt.date() and lengu == 0:
                sql = "INSERT INTO sonntagsfrage(" + fields + ") VALUES(" + sqlinfos[i] + ");"
                db.execute(sql)
                con.commit()
                print(ins + "-Daten wurden neu angelegt.")
            elif today > datedt.date() and lengu != 0:
                sql = "UPDATE sonntagsfrage SET cdu = '" + table[i][2] + "', spd = '" + table[i][3] + "', gru = '" + \
                      table[i][
                          4] + "', fdp = '" + table[i][5] + "', lin = '" + table[i][6] + "', afd = '" + table[i][
                          7] + "', son = '" + \
                      table[i][8] + "' WHERE institut = '" + ins + "'; "
                db.execute(sql)
                con.commit()
                print(ins + "-Daten erneuert.")
                chgbool = True
            sql = "INSERT OR IGNORE INTO " + ins + "(datum,cdu,spd,gru,fdp,lin,afd,son) VALUES (" + sqlinfos[
                i].replace("'" + ins + "', ", "") + ");"
            db.execute(sql)
            con.commit()
        if chgbool:
            sql = "UPDATE sonntagsfrage SET datum ='" + str(today) + "' WHERE institut='update';"
            db.execute(sql)
            con.commit()
        else:
            print("Keine neuen Daten!")
    else:
        print("Hier Drawmodus")
        institute = ['Allensbach', 'Kantar', 'Forsa', 'Politbarometer', 'GMS', 'dimap', 'insa', 'yougov']
        parteien = ['cdu', 'spd', 'gru', 'fdp', 'lin', 'afd', 'son']
        parcl = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 1), (0, 0.5, 1), (0.4, 0.4, 0.4)]
        plts = {}
        for institut in institute:
            institutdict = {}
            for partei in parteien:
                sql = "SELECT " + partei + " FROM " + institut + " ORDER BY datum DESC;"
                erg = db.execute(sql).fetchall()
                institutdict[partei] = erg
            plts[institut] = institutdict
        for institut in institute:
            for partei in parteien:
                for i in range(len(plts[institut][partei])):
                    plts[institut][partei][i] = plts[institut][partei][i][0]
        fig, axs = plt.subplots(2, 4)
        fig.suptitle('Sonntagsfrage', fontsize=30)
        k = 0
        j = 0
        for institut in institute:
            pltpart = []
            sql = "SELECT datum FROM " + institut + " ORDER BY datum DESC;"
            erg = db.execute(sql).fetchall()
            for i in range(len(erg)):
                erg[i] = erg[i][0]
            erg = sorted([datetime.strptime(dt, "%d.%m.%Y") for dt in erg])
            for i in range(len(erg)):
                erg[i] = erg[i].strftime("%d.%m.%Y")
            for partei in parteien:
                pltpart.append(list(map(int, list(map(float, plts[institut][partei])))))
            parte = axs[j][k]
            j += 1 if k == 3 else 0
            k = 0 if k == 3 else k + 1
            parte.set_title(institut, fontsize=20)
            n = 0
            ytick = np.arange(0, 30, 5)
            for i in pltpart:
                parte.plot(erg, i, label=parteien[n], color=parcl[n])
                parte.set_ylim([0, 30])
                parte.set_xticklabels(erg, fontsize=7)
                parte.set_yticklabels(ytick, fontsize=7)
                n += 1
        mng = plt.get_current_fig_manager()
        mng.window.state('zoomed')
        handles, labels = axs[0][0].get_legend_handles_labels()
        axs[0][3].legend(handles, labels, loc='upper right', bbox_to_anchor=(1.5, 1.05))
        plt.show()


if __name__ == "__main__":
    main()
