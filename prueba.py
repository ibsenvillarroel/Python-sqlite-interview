from cProfile import label
import sqlite3
from turtle import color
import matplotlib.pyplot as plt 
import numpy as np 
import pandas as pd 

#para probar cada una de las funciones, descomentar el llamado a las mismas 
#para los graficos solo descomentar el plt.show()

conn = sqlite3.connect("database.sqlite")


###Crea una consulta básica sobre la tabla Country
def consulta_basica():
    cursor = conn.cursor()
    instruccion = f"SELECT * FROM country "
    cursor.execute(instruccion)
    datos = cursor.fetchall()
    conn.commit()
    conn.close()
    print(datos)
#consulta_basica()     

###Une la tabla Country con la tabla League para saber que liga corresponde a cada país
def union_country_league():
    cursor = conn.cursor()
    instruccion = f"SELECT  b.name Pais, a.name Liga FROM country a, league b where a.id = b.id"
    cursor.execute(instruccion)
    datos = cursor.fetchall()
    conn.commit()
    conn.close()
    print(datos)
#union_country_league() 


### Crea una consulta con las siguientes tablas - Match, Country, League, Team - donde veamos la siguiente información 
### de cada uno de los partidos jugados en España country_name =”Spain”
### Match.id, Country.name, League.name, season, stage, date, Team.team_long_name (nombre del equipo local), 
### Team.team_long_name(nombre del equipo visitante), home_team_goal, away_team_goal
### Los registros deben estar ordenados por fecha

def partidos_spain():
    cursor = conn.cursor()
    instruccion =f'''with cte 
    as 
    (SELECT  a.id, b.name nombre, c.name, a.season, a.stage, a.date, d.team_long_name, a.home_team_goal, a.away_team_api_id, a.away_team_goal 
    FROM match a, country b, league c, team d 
    where a.country_id = b.id and a.league_id = c.id and b.id = c.id and a.home_team_api_id = d.team_api_id and b.name = 'Spain')
    select a.id, nombre, name, season, stage, date, a.team_long_name, home_team_goal, b.team_long_name, away_team_goal 
    from cte a, team b
    where  away_team_api_id = b.team_api_id
    order by date'''
    cursor.execute(instruccion)
    datos = cursor.fetchall()
    conn.commit()
    conn.close()
    print(datos)
#partidos_spain()

###Utilizando las mismas tablas de la consulta anterior, queremos encontrar varias estadísticas para cada uno de los siguientes paises 
### country_name : ('Spain', 'Germany', 'France', 'Italy', 'England'). Queremos agregar esta informacion por pais, liga y temporada (season).
### Las estadisticas que queremos ver son:
### número de jornadas (stages)  → number_of_stages,
### número de equipos → number_of_teams,
### media de goles por equipo local → avg_home_team_scors, 
### media de goles por equipo visitante → avg_away_team_goals, 
### media de diferencia de goles → avg_goal_dif, 
### media de goles por partido → avg_goals, 
### número total de goles → total_goals
### Filtrar eliminando los registros que tengan menos de 10 jornadas
### Ordenar por nombre del pais, nombre de la liga y temporada de manera descendiente

def estadisticas_pais_temporada():
    cursor = conn.cursor()
    instruccion =f'''with cte as
    (SELECT   b.name nombre, c.name, a.season, max(a.stage) stage, count(distinct(a.home_team_api_id)) home_team_api_id, 
    avg(a.home_team_goal) home_team_goal, avg(a.away_team_goal)away_team_goal, 
    avg(a.home_team_goal - a.away_team_goal) dif_goal, avg(a.home_team_goal + a.away_team_goal) avg_goal, 
    sum(a.home_team_goal + a.away_team_goal) total_goal
    FROM match a, country b, league c, team d 
    where a.country_id = b.id 
    and a.league_id = c.id 
    and b.id = c.id 
    and a.home_team_api_id = d.team_api_id 
    and nombre in ('Spain', 'Germany', 'France', 'Italy', 'England')
    group by nombre, season
    order by nombre, c.name, a.season desc)
    select  nombre, name, season, stage, home_team_api_id, home_team_goal, away_team_goal, dif_goal, avg_goal, total_goal 
    from cte
    where stage >=10
    '''
    cursor.execute(instruccion)
    datos = cursor.fetchall()
    conn.commit()
    conn.close()
    print(datos)
#estadisticas_pais_temporada()

#esta funcion es por si se quiere tener las mismas estadisticas por pais y temporada, solo hay que colocar esos 2 parametros 
def estadisticas_pais_temporada2(pais, temporada):
    cursor = conn.cursor()
    instruccion =f'''SELECT   b.name nombre, c.name, a.season, max(a.stage), count(distinct(a.home_team_api_id)), avg(a.home_team_goal), avg(a.away_team_goal), 
    avg(a.home_team_goal - a.away_team_goal), avg(a.home_team_goal + a.away_team_goal), sum(a.home_team_goal + a.away_team_goal)
    FROM match a, country b, league c, team d 
    where a.country_id = b.id 
    and a.league_id = c.id 
    and b.id = c.id 
    and a.home_team_api_id = d.team_api_id 
    and nombre = {pais}
    and a.season = {temporada}
    '''
    cursor.execute(instruccion)
    datos = cursor.fetchall()
    conn.commit()
    conn.close()
    print(datos)
#estadisticas_pais_temporada2("'England'","'2015/2016'")


###Crear varios graficos donde se puedan ver la media de goles por partido en las diferentes ligas (matplotlib utilizado)
xspain = pd.read_sql_query(f'''SELECT a.stage
FROM match a, country b, league c, team d 
where a.country_id = b.id 
and a.league_id = c.id 
and b.id = c.id 
and a.home_team_api_id = d.team_api_id
and b.name = 'Spain' 
group by a.stage''', conn)
yspain = pd.read_sql_query(f'''SELECT avg(a.home_team_goal + a.away_team_goal)
FROM match a, country b, league c, team d 
where a.country_id = b.id 
and a.league_id = c.id 
and b.id = c.id 
and a.home_team_api_id = d.team_api_id
and b.name = 'Spain' 
group by a.stage''', conn)
#plt.plot(xspain, yspain)
#plt.show()    

xgermany = pd.read_sql_query(f'''SELECT a.stage
FROM match a, country b, league c, team d 
where a.country_id = b.id 
and a.league_id = c.id 
and b.id = c.id 
and a.home_team_api_id = d.team_api_id
and b.name = 'Germany' 
group by a.stage''', conn)
ygermany = pd.read_sql_query(f'''SELECT avg(a.home_team_goal + a.away_team_goal)
FROM match a, country b, league c, team d 
where a.country_id = b.id 
and a.league_id = c.id 
and b.id = c.id 
and a.home_team_api_id = d.team_api_id
and b.name = 'Germany' 
group by a.stage''', conn)
#plt.plot(xgermany, ygermany)
#plt.show()   

xfrance = pd.read_sql_query(f'''SELECT a.stage
FROM match a, country b, league c, team d 
where a.country_id = b.id 
and a.league_id = c.id 
and b.id = c.id 
and a.home_team_api_id = d.team_api_id
and b.name = 'France' 
group by a.stage''', conn)
yfrance = pd.read_sql_query(f'''SELECT avg(a.home_team_goal + a.away_team_goal)
FROM match a, country b, league c, team d 
where a.country_id = b.id 
and a.league_id = c.id 
and b.id = c.id 
and a.home_team_api_id = d.team_api_id
and b.name = 'France' 
group by a.stage''', conn)
#plt.plot(xfrance, yfrance)
#plt.show() 

xitaly = pd.read_sql_query(f'''SELECT a.stage
FROM match a, country b, league c, team d 
where a.country_id = b.id 
and a.league_id = c.id 
and b.id = c.id 
and a.home_team_api_id = d.team_api_id
and b.name = 'Italy' 
group by a.stage''', conn)
yitaly = pd.read_sql_query(f'''SELECT avg(a.home_team_goal + a.away_team_goal)
FROM match a, country b, league c, team d 
where a.country_id = b.id 
and a.league_id = c.id 
and b.id = c.id 
and a.home_team_api_id = d.team_api_id
and b.name = 'Italy' 
group by a.stage''', conn)
#plt.plot(xitaly, yitaly)
#plt.show()   

xengland = pd.read_sql_query(f'''SELECT a.stage
FROM match a, country b, league c, team d 
where a.country_id = b.id 
and a.league_id = c.id 
and b.id = c.id 
and a.home_team_api_id = d.team_api_id
and b.name = 'England' 
group by a.stage''', conn)
yengland = pd.read_sql_query(f'''SELECT avg(a.home_team_goal + a.away_team_goal)
FROM match a, country b, league c, team d 
where a.country_id = b.id 
and a.league_id = c.id 
and b.id = c.id 
and a.home_team_api_id = d.team_api_id
and b.name = 'England' 
group by a.stage''', conn)

plt.figure(figsize=(10, 6))

plt.plot(xspain, yspain, color='violet', label= 'Spain')
plt.plot(xgermany, ygermany, color='g', label='Germany')
plt.plot(xfrance, yfrance, color='y', label='France')
plt.plot(xitaly, yitaly, color='red', label ='Italy')
plt.plot(xengland, yengland, color='blue', label= 'England')

plt.xlabel('Jornada')
plt.ylabel('Promedio Goles')
plt.title('Promedio de goles por jornada y pais')
plt.legend(loc='upper left')

plt.show()

###Juntar las tablas PLAYER donde cada registro es un jugador, con la tabla Player_Attributes, donde cada registro es un jugador/temporada.
###Para ello:
###Crear una subquery  de la tabla Player_Attributes donde se agrupan los atributos de cada jugador en un solo registro:
###media del rating: overall_rating
###media del potencial: potential
###Unir esta tabla a la tabla principal PLAYER, utilizando left join

def join_player():
    cursor = conn.cursor()
    instruccion = f''' with cte as (SELECT player_fifa_api_id,  avg(overall_rating) avg_overall_rating, avg(potential) avg_potential
    FROM player_attributes
    group by player_fifa_api_id)

    select *
    from player a
    left join cte b
    on a.player_fifa_api_id = b.player_fifa_api_id
    
    '''
    cursor.execute(instruccion)
    datos = cursor.fetchall()
    conn.commit()
    conn.close()
    print(datos)

#join_player()    