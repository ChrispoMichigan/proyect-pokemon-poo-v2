from __future__ import annotations
import random 
from abc import ABC, abstractmethod 
from typing import List, Optional, Tuple
import os
import sqlite3
import json


'''
#*
#* Todas las operaciónes de la base de datos
#*
'''
class DataBase:
    def __init__(self) -> None:
        self.conexion = sqlite3.connect('pokedex.db')
        self.cursor = self.conexion.cursor()
        self.__init_tables()

    def __init_tables(self):
        # Tabla de usuarios
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user VARCHAR(50) NOT NULL UNIQUE,
                update_at DATETIME DEFAULT (datetime('now', 'localtime'))
            )
            """)
        
        # Tabla de pokémons
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pokemons(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description VARCHAR(255),
                evolution INTEGER DEFAULT 1,
                type VARCHAR(20) CHECK(type IN ('Agua', 'Fuego', 'Electrico', 'Hierba')),
                damage INTEGER NOT NULL,
                defense INTEGER NOT NULL,
                health INTEGER NOT NULL,
                level INTEGER DEFAULT 1,
                evolution_names TEXT NOT NULL
            )
            """)
        
        # Tabla intermedia usuario-pokémons
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_pokemons(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_user INTEGER NOT NULL,
                id_pokemon INTEGER NOT NULL,
                FOREIGN KEY (id_user) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (id_pokemon) REFERENCES pokemons(id) ON DELETE CASCADE
            )
            """)
        
        # Tabla de batallas
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS battles(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_user INTEGER NOT NULL,
                txt_route VARCHAR(500) NOT NULL,
                created_at DATETIME DEFAULT (datetime('now', 'localtime')),
                FOREIGN KEY (id_user) REFERENCES users(id) ON DELETE CASCADE
            )
            """)
        
        # Confirmar cambios
        self.conexion.commit()

    def get_all_users(self) -> List[Tuple]:
        self.cursor.execute('SELECT * FROM users')
        partidas = self.cursor.fetchall()
        return partidas
    
    def post_new_user(self, user : str) -> Tuple | None:
        self.cursor.execute("INSERT INTO users (user) VALUES(?)", (user,))
        self.conexion.commit()
        user_id = self.cursor.lastrowid

        if user_id is None:
            return None
        
        return self.get_user_by_id(user_id)

    def get_user_by_id(self, id : int) -> Tuple:
        self.cursor.execute("SELECT id, user, update_at FROM users WHERE id = ?", (id,))
        usuario = self.cursor.fetchone()
        return usuario
    
    def get_user_by_name(self, name : str) -> Tuple:
        self.cursor.execute("SELECT id, user, update_at FROM users WHERE user = ?", (name,))
        usuario = self.cursor.fetchone()
        return usuario
    
    def post_pokemon_by_id_user(self, id_user : int, pokemon : Agua | Electrico | Fuego | Hierba):

        evolution_names_json = json.dumps(pokemon.evoluciones_nombres)

        self.cursor.execute("INSERT INTO pokemons (name, description, evolution, type, damage, defense, health, level, evolution_names) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (
                pokemon.nombre,
                pokemon.descripcion,
                pokemon.evolucion,
                pokemon.tipo,
                pokemon.ataque,
                pokemon.defensa,
                pokemon.vida,
                pokemon.nivel,
                evolution_names_json
            )
        )
        self.conexion.commit()
        pokemon_id = self.cursor.lastrowid

        if pokemon_id is None:
            return
        
        self.cursor.execute("INSERT INTO user_pokemons (id_user, id_pokemon) VALUES(?, ?)", (id_user, pokemon_id,))
        self.conexion.commit()

    def get_pokemon_by_id(self, id_pokemon : int) -> Tuple:
        self.cursor.execute("SELECT * FROM pokemons WHERE id = ?", (id_pokemon,))
        pokemon = self.cursor.fetchone()
        return pokemon
    
    def get_all_pokemons_by_user_id(self, id_user: int) -> List[Tuple]:
        self.cursor.execute("""
            SELECT p.id, p.name, p.description, p.evolution, p.type, p.damage, p.defense, p.health, p.level, p.evolution_names
            FROM pokemons p
            INNER JOIN user_pokemons up ON p.id = up.id_pokemon
            WHERE up.id_user = ?
        """, (id_user,))
        pokemons = self.cursor.fetchall()
        return pokemons
    
    def delete_user_by_id(self, id_user: int):

        pokemons = self.get_all_pokemons_by_user_id(id_user)
        for pokemon in pokemons:
            self.cursor.execute("DELETE FROM pokemons WHERE id = ?", (pokemon[0],))
            self.conexion.commit()

        self.cursor.execute("DELETE FROM users WHERE id = ?", (id_user,))
        self.conexion.commit()

        self.cursor.execute("DELETE FROM user_pokemons WHERE id_user = ?", (id_user,))
        self.conexion.commit()

    def put_pokemon_by_id(self, pokemon : Agua | Electrico | Fuego | Hierba):
        if pokemon.pokemon_id is None:
            print("Error: El pokémon no tiene un ID válido para actualizar")
            return
    
        evolution_names_json = json.dumps(pokemon.evoluciones_nombres)
        
        self.cursor.execute("""
            UPDATE pokemons 
            SET name = ?, 
                description = ?, 
                evolution = ?, 
                type = ?, 
                damage = ?, 
                defense = ?, 
                health = ?, 
                level = ?, 
                evolution_names = ?
            WHERE id = ?
        """, (
            pokemon.nombre,
            pokemon.descripcion,
            pokemon.evolucion,
            pokemon.tipo,
            pokemon.ataque,
            pokemon.defensa,
            pokemon.vida,
            pokemon.nivel,
            evolution_names_json,
            pokemon.pokemon_id
        ))
        
        self.conexion.commit()

    def put_user_update_by_id(self, user_id):
        self.cursor.execute("""
            UPDATE users 
            SET update_at = datetime('now', 'localtime')
            WHERE id = ?
        """, (
            user_id,
        ))            

        self.conexion.commit()
class Utils:
    @staticmethod 
    def clear():
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def pause():
        try:
            input("\nPresiona Enter para continuar..")
        except Exception:
            pass

    @staticmethod
    def print_title(t: str):
        print("=" * 60 )
        print(t.center(60))
        print("=" * 60)


#clase base abstracta 
class PokemonBase(ABC):
    def __init__(self,
        nombre: str = "Sin Pokemon",
        descripcion: str = "No descripcin",
        ataque: int = 0,
        defensa: int = 0,
        vida: int = 0,
        nivel: int = 1,
        evolucion: int = 1,
        atrapado: bool = False,
        pokemon_id: int | None = None
        ):

        self.pokemon_id = pokemon_id
        self.nombre: str = nombre
        self.descripcion: str = descripcion
        self.ataque: int = max(0, int(ataque))
        self.defensa: int = max(0, int(defensa))
        self.vida: int = max(0, int(vida))
        self.nivel: int = max(1, int(nivel))
        self.evolucion: int = max(1, int(evolucion))
        if self.evolucion > 3:
            self.evolucion = 3
        self.atrapado: bool =  bool (atrapado)

    @abstractmethod
    def hablar(self):
        raise NotImplementedError

    @abstractmethod
    def actualizar(self):
        raise NotImplementedError

    @abstractmethod
    def detallesPokemon(self):
        raise NotImplementedError

    def subir_nivel(self, inc: int = 10, reiniciar_on_evol: bool = True):#si alcanza 100 intenta evolucionar hasta 3 evoluciones
        self.nivel += inc
        if self.nivel >= 100:
            if self.evolucion < 3:
                self.evolucion += 1
                if reiniciar_on_evol:
                    self.nivel = 0
                return True 
            else:
                self.nivel = 0
        return False


#Entrenamiento abstracto
class Entrenamiento(ABC):
    @abstractmethod
    def subirAtaque(self):
        raise NotImplementedError

    @abstractmethod
    def subirDefensa(self):
        raise NotImplementedError

    @abstractmethod
    def subirVida(self):
        raise NotImplementedError
        
#Clase Pokemon

class Pokemon(PokemonBase):
    BOOST_ATAQUE = 20 
    BOOST_DEFENSA = 20
    BOOST_VIDA = 20

    def __init__(self,
        nombre: str = "Sin Pokemon",
        descripcion: str = "No descripcion",
        ataque: int = 0,
        defensa: int = 0,
        vida: int = 0,
        nivel: int = 1,
        evolucion: int = 1,
        atrapado: bool = False,
        evoluciones_nombres: Optional[List[str]] = None,
        pokemon_id: int | None = None
        ):
        
        super().__init__(nombre, descripcion, ataque, defensa, vida, nivel, evolucion, atrapado, pokemon_id)

        if evoluciones_nombres:
            self.evoluciones_nombres = evoluciones_nombres[:3]
        else:
            self.evoluciones_nombres = [self.nombre]

        if self.nombre == "Sin Pokemon" and 1 <= self.evolucion <= len(self.evoluciones_nombres):
            self.nombre = self.evoluciones_nombres[self.evolucion - 1]

    def detallesPokemon(self):
        Utils.print_title("DETALLES DEL POKEMON")
        print(f"Nombre         : {self.nombre}")
        print(f"Descripcion    : {self.descripcion}")    
        print(f"Ataque         : {self.ataque}")    
        print(f"Defensa        : {self.defensa}")
        print(f"Vida           : {self.vida}")
        print(f"Nivel          : {self.nivel}")
        print(f"Evolucion      : {self.evolucion}")
        print(f"Atrapado   : {'Sí' if self.atrapado else 'No'}")

    
    def mostrar_datos(self):
        print("\t--- ESTADISTICAS ACTUALES ---")
        print(f"Nombre: {self.nombre} | Ataque: {self.ataque} | Defensa: {self.defensa} | Vida: {self.vida} | Nivel: {self.nivel}")

    def hablar(self):
        print(f"{self.nombre}! {self.nombre}!")

    def entrenar(self):
        self.ataque += 10
        self.defensa += 10
        self.vida += 10
        evoluciono = self.subir_nivel(10)
        if evoluciono:
            # actualizar nombre si existe en lista
            idx = min(self.evolucion - 1, len(self.evoluciones_nombres) - 1)
            self.nombre = self.evoluciones_nombres[idx]
            print(f"¡El Pokemon ha evolucionado! Ahora es: {self.nombre}")
        else:
            print("Entrenamiento aplicado.")

#metodos individuales
    def subirAtaque(self):
        self.ataque += self.BOOST_ATAQUE
        print(f"Ataque aumentada a {self.ataque}")

    def subirDefensa(self):
        self.defensa += self.BOOST_DEFENSA
        print(f"Defensa aumentada a {self.defensa}")

    def subirVida(self):
        self.vida += self.BOOST_VIDA
        print(f"Vida aumentada a {self.vida}")

    def actualizar(self):
        self.ataque += self.BOOST_ATAQUE
        self.defensa += self.BOOST_DEFENSA
        self.vida += self.BOOST_VIDA
        self.evoluciono = self.subir_nivel(0)
        print(f"Actualizacion completa: ataque, defensa y vida incrementados.")

#subclases especializadas

class Agua(Pokemon):

    def __init__(self, 
                nombre: str = "Sin Pokemon", 
                descripcion: str = "No descripcion", 
                ataque: int = 0, 
                defensa: int = 0, 
                vida: int = 0, 
                nivel: int = 1,
                evolucion: int = 1, 
                atrapado: bool = False, 
                evoluciones_nombres: List[str] | None = ["Squirtle", "Wartortle", "Blastoise"], 
                pokemon_id: int | None = None,
                ataque_especial="Hidrobomba"
            ):
        super().__init__(nombre, descripcion, ataque, defensa, vida, nivel, evolucion, atrapado, evoluciones_nombres, pokemon_id)

        self.ataque_especial = ataque_especial
        self.tipo = 'Agua'

    def actualizar(self):
        self.defensa += 10
        print(f"{self.nombre} (Agua) se refresca: +10 defensa.")

class Fuego(Pokemon):

    def __init__(self, 
                nombre: str = "Sin Pokemon", 
                descripcion: str = "No descripcion", 
                ataque: int = 0, 
                defensa: int = 0, 
                vida: int = 0, 
                nivel: int = 1,
                evolucion: int = 1, 
                atrapado: bool = False, 
                evoluciones_nombres: List[str] | None = ["Charmander", "Charmeleon", "Charizard"], 
                pokemon_id: int | None = None,
                ataque_especial: str = "Lanzallamas"
            ):
        super().__init__(nombre, descripcion, ataque, defensa, vida, nivel, evolucion, atrapado, evoluciones_nombres, pokemon_id)

        self.ataque_especial = ataque_especial
        self.tipo = 'Fuego'

    def actualizar(self):
        self.ataque += 10
        print(f"{self.nombre} (Fuego) se enciende: +10 ataque.")


class Electrico(Pokemon):

    def __init__(self, 
                nombre: str = "Sin Pokemon", 
                descripcion: str = "No descripcion", 
                ataque: int = 0, 
                defensa: int = 0, 
                vida: int = 0, 
                nivel: int = 1,
                evolucion: int = 1, 
                atrapado: bool = False, 
                evoluciones_nombres: List[str] | None = ["Pichu", "Pikachu", "Raichu"], 
                pokemon_id: int | None = None,
                ataque_especial: str = "Impactrueno"
            ):
        super().__init__(nombre, descripcion, ataque, defensa, vida, nivel, evolucion, atrapado, evoluciones_nombres, pokemon_id)

        self.ataque_especial = ataque_especial
        self.tipo = 'Electrico'

    def actualizar(self):
        self.vida += 10
        print(f"{self.nombre} (Electrico) se carga: +10 vida.")

class Hierba(Pokemon):

    def __init__(self, 
                nombre: str = "Sin Pokemon", 
                descripcion: str = "No descripcion", 
                ataque: int = 0, 
                defensa: int = 0, 
                vida: int = 0, 
                nivel: int = 1,
                evolucion: int = 1, 
                atrapado: bool = False, 
                evoluciones_nombres: List[str] | None = ["Bulbasaur", "Ivysaur", "Venusaur"], 
                pokemon_id: int | None = None,
                ataque_especial: str = "Rayo Solar"
            ):
        super().__init__(nombre, descripcion, ataque, defensa, vida, nivel, evolucion, atrapado, evoluciones_nombres, pokemon_id)

        self.ataque_especial = ataque_especial
        self.tipo = 'Hierba'

    def actualizar(self):
        self.ataque += 5
        self.vida += 5
        print(f"{self.nombre} (Hierba) se nutre: +5 ataque, +5 vida.")


#herencia multiple pokemonn con entrenamiento

class PokemonConEntrenamiento(Pokemon, Entrenamiento):
    def subirAtaque(self):
        Pokemon.subirAtaque(self)

    def subirDefensa(self):
        Pokemon.subirDefensa(self)

    def subirVida(self):
        Pokemon.subirVida(self)

#sistema de combate

def aplicar_daño(atacante_val: int, defensor_def: int, defensor_vida: int) -> Tuple[int, int]:
        # atacando defensa
    resta = atacante_val
    if defensor_def >= resta:
        defensor_def -= resta
    else:
        sobrante = resta - defensor_def
        defensor_def = 0
        defensor_vida -= sobrante
        if defensor_vida < 0:
            defensor_vida = 0
    return defensor_def, defensor_vida

#clase app 

class App:
    def __init__(self):
        self.id_jugador : int
        self.jugador_nombre: str = ""
        self.mi_pokemon: Agua | Fuego | Electrico | Hierba | None = None
        self.pokemons_atrapados : List[Agua | Fuego | Electrico | Hierba] = []
        #enemigos por defecto 2 debiles y 2 fuertes
        self.enemigos: List[Agua | Fuego | Electrico | Hierba] = self._crear_enemigos_por_defecto()

        # Crear base de datos
        self.database = DataBase()
        Utils.clear()
        self.__init_app()
        self.main_loop()

    def __init_app(self):
        self.__bienvenida()

        if len(self.database.get_all_users()) == 0:
            Utils.print_title('No existen partidas guardas, crea una')
            Utils.pause()
            Utils.clear()
            self.__crear_usuario()
        else:
            self.__seleccionar_guardado()
            self.__cargar_pokemos_desde_db()

        Utils.clear()

    def __cargar_pokemos_desde_db(self):
        pokemons_db = self.database.get_all_pokemons_by_user_id(self.id_jugador)
        pokemons = []

        if len(pokemons_db) == 0:
            self.elegir_inicial()
            return
        
        for pokemon in pokemons_db:
            if pokemon[4] == 'Agua':
                pokemon = Agua(
                    nombre=pokemon[1],
                    descripcion=pokemon[2],
                    ataque=pokemon[5],
                    defensa=pokemon[6],
                    vida=pokemon[7],
                    nivel=pokemon[8],
                    evolucion=pokemon[3],
                    atrapado=True,
                    evoluciones_nombres=json.loads(pokemon[9]),
                    pokemon_id=pokemon[0]
                )
                pokemons.append(pokemon)
                continue
            if pokemon[4] == 'Fuego':
                pokemon = Fuego(
                    nombre=pokemon[1],
                    descripcion=pokemon[2],
                    ataque=pokemon[5],
                    defensa=pokemon[6],
                    vida=pokemon[7],
                    nivel=pokemon[8],
                    evolucion=pokemon[3],
                    atrapado=True,
                    evoluciones_nombres=json.loads(pokemon[9]),
                    pokemon_id=pokemon[0]
                )
                pokemons.append(pokemon)
                continue
            if pokemon[4] == 'Hierba':
                pokemon = Hierba(
                    nombre=pokemon[1],
                    descripcion=pokemon[2],
                    ataque=pokemon[5],
                    defensa=pokemon[6],
                    vida=pokemon[7],
                    nivel=pokemon[8],
                    evolucion=pokemon[3],
                    atrapado=True,
                    evoluciones_nombres=json.loads(pokemon[9]),
                    pokemon_id=pokemon[0]
                )
                pokemons.append(pokemon)
                continue
            if pokemon[4] == 'Electrico':
                pokemon = Electrico(
                    nombre=pokemon[1],
                    descripcion=pokemon[2],
                    ataque=pokemon[5],
                    defensa=pokemon[6],
                    vida=pokemon[7],
                    nivel=pokemon[8],
                    evolucion=pokemon[3],
                    atrapado=True,
                    evoluciones_nombres=json.loads(pokemon[9]),
                    pokemon_id=pokemon[0]
                )
                pokemons.append(pokemon)
                continue

        self.mi_pokemon = pokemons[0]
        del pokemons[0]
        self.pokemons_atrapados = pokemons

        Utils.print_title('Pokemones cargados')
        for pokemon in pokemons_db:
            Utils.print_title(f'Nombre: {pokemon[1]} | Ataque: {pokemon[5]} | Defensa {pokemon[6]} | Vida: {pokemon[7]} | Nivel: {pokemon[8]}')
        Utils.pause()
        Utils.clear()

    def __seleccionar_guardado(self):
        while True:
            usuarios = self.database.get_all_users()
            Utils.print_title('Seleccione una partida')
            for i, usuario in enumerate(usuarios):
                print(f'[{i + 1}] - {usuario[1]} - {usuario[2]}')

            print(f'[{len(usuarios) + 1}] - Crear nueva partida')
            print(f'[{len(usuarios) + 2}] - Eliminar una partida')

            try:
                user_option = int(input('Seleccione el usuario\t'))
                if user_option > 0 and user_option <= len(usuarios) + 2:
                    if len(usuarios) + 2 == user_option:
                        Utils.clear()
                        self.__eliminar_partida()
                        Utils.clear()
                        continue
                    break
                raise ValueError
            except ValueError:
                print('Selccione una opción válida')
                Utils.pause()
                Utils.clear()

        if len(usuarios) + 1 == user_option:
            Utils.clear()
            self.__crear_usuario()
        else:
            self.id_jugador = usuarios[user_option - 1][0]
            self.jugador_nombre = usuarios[user_option - 1][1]
            Utils.print_title('Usuario cargado correctamente')
            print(f'¡Bienvenido de nuevo {self.jugador_nombre}')
            Utils.pause()
            Utils.clear()

    def __eliminar_partida(self):
        usuarios = self.database.get_all_users()
        Utils.print_title('Seleccione una partida a eliminar')

        while True:
            for i, usuario in enumerate(usuarios):
                print(f'[{i + 1}] - {usuario[1]} - {usuario[2]}')

            print(f'[{len(usuarios) + 1}] - Cancelar')
            try:
                user_delete = int(input('Seleccione el usuario\t'))
                if user_delete > 0 and user_delete <= len(usuarios) + 1:
                    break
                raise ValueError
            except ValueError:
                print('Selccione una opción válida')
                Utils.pause()
                Utils.clear()

        if user_delete > 0 and user_delete <= len(usuarios):
            self.database.delete_user_by_id(usuarios[user_delete - 1][0])
            Utils.print_title('Usuario borrado correctamente')
            Utils.pause()

    def __crear_usuario(self):
        nombre = ''
        while True:
 
            nombre = input("Ingresa tu nombre:\t").strip()

            if nombre == '':
                print('Inserte un nombre de usuario válido')
                Utils.pause()
                Utils.clear()
                continue

            user_found = self.database.get_user_by_name(nombre)
            
            if user_found is None:
                break
            Utils.print_title('Este usuarios ya existe, escriba otro')
            Utils.pause()
            Utils.clear()

        new_user = self.database.post_new_user(nombre)
        
        if new_user is None:
            return

        self.id_jugador = new_user[0]
        self.jugador_nombre = new_user[1]
        print(f"\nHola, {self.jugador_nombre}! Aun no tienes Pokemon. Debes elegir uno.")
        Utils.pause()
        Utils.clear()
        self.elegir_inicial()

    def __bienvenida(self):
        Utils.print_title("Bienvenido a la POKEDEX")
        Utils.pause()
        Utils.clear()

    def elegir_inicial(self):
        Utils.print_title("Elege tu Pokemon inicial")
        opciones = [
            ("Agua", Agua("Squirtle", "Pokemon tortuga", ataque=20, defensa=30, vida=100, nivel=1, evoluciones_nombres=["Squirtle", "Wartortle", "Blastoise"])),
            ("Fuego", Fuego("Charmander", "Pokemon de fuego", ataque=25, defensa=20, vida=90, nivel=1, evoluciones_nombres=["Charmander", "Charmeleon", "Charizard"])),
            ("Electrico", Electrico("Pichu", "Poemon electrico", ataque=18, defensa=18, vida=80, nivel=1, evoluciones_nombres=["Pichu", "Pikachu", "Raichu"])),
            ("Hierba", Hierba("Bulbasaur", "Pokemon planta", ataque=22, defensa=22, vida=95, nivel=1, evoluciones_nombres=["Bulbasaur", "Ivysaur", "Venusaur"]))
        ]
        for idx, (tipo, poke) in enumerate(opciones, start = 1):
            print(f"{idx}. {tipo} - {poke.nombre} - Ataque {poke.ataque} | Defensa {poke.defensa} | Vida {poke.vida}")
        print("0. Salir")
        while True:
            try:
                sel = int(input("Selecciona el numero del Pokemon que deseas:  "))
                if sel == 0:
                    print("Saliendo...")
                    exit(0)
                if 1 <= sel <= len(opciones):
                    self.mi_pokemon = opciones[sel - 1][1]

                    # Añadir pokemon a jugador en la base de datos
                    self.database.post_pokemon_by_id_user(self.id_jugador, opciones[sel - 1][1])
                    
                    if self.mi_pokemon is None:
                        raise ValueError

                    print(f"\nHas elegido a {self.mi_pokemon.nombre}!")
                    Utils.pause()
                    Utils.clear()
                    self.mi_pokemon.detallesPokemon()
                    Utils.pause()
                    Utils.clear()
                    break
            except ValueError:
                print("Ingresa un numero valido.")

    def _crear_enemigos_por_defecto(self) -> List[Agua | Fuego | Electrico | Hierba]:
        e1 = Fuego("Enemigo Fuerte 1", "Firme y peligroso", ataque=80, defensa=80, vida=200, nivel=50)
        e2 = Electrico("Enemigo Fuerte 2", "Agil y potente", ataque=70, defensa=60, vida=180, nivel=48)
        e3 = Hierba("Enemigo Debil 1", "Tranquilo", ataque=20, defensa=20, vida=80, nivel=5)
        e4 = Agua("Enemigo Debil 2", "Aguas calmadas", ataque=15, defensa=18, vida=70, nivel=4)
        return [e1, e2, e3, e4]

    def main_loop(self):
        while True:
            Utils.print_title("MENU PRINCIPAL")
            print("1. Detalles de mi Pokemon")
            print("2. Hablar Pokemon")
            print("3. Entrenamiento ")
            print("4. Combatir")
            print("5. Crear enemigo personalizado")
            print("6. Ver Pokemon Atrapado")
            print("7. Pruebas de Manejo de errores")
            print("8. Registros de batallas")
            print("9. Guardar partida")
            print("10. Salir")
            try:
                op = int(input("Elige una opcion:  "))
                if op < 1 or op > 10:
                    raise ValueError
            except ValueError:
                print("Ingresa un numero valido")
                Utils.pause()
                Utils.clear()
                continue

            Utils.clear()
            if op == 1:
                if self.mi_pokemon:
                    self.mi_pokemon.detallesPokemon()
                    Utils.pause()
                else:
                    print("No tienes Pokemon.")
                    Utils.pause()

            elif op == 2:
                if self.mi_pokemon:
                    self.mi_pokemon.hablar()
                    Utils.pause()
                else:
                    print("No tienes Pokemon.")
                    Utils.pause()

            elif op == 3:
                if self.mi_pokemon:
                    self.menu_entrenamiento()
                    Utils.pause()
                else:
                    print("No tienes Pokemon.")
                    Utils.pause()

            elif op == 4:
                if self.mi_pokemon:
                    self.menu_combatir()
                    Utils.pause()
                else:
                    print("No tienes Pokemon.")
                    Utils.pause()

            elif op == 5:
                self.crear_pokemon_enemigo_manual()

            elif op == 6:
                self.VerPokemonsAtrapados()
                
            elif op == 7:
                self.pruebas_manejo_errores()

            elif op == 8:
                pass
            
            elif op == 9:
                self.__guardar_partida()

            elif op == 10:
                print("Gracias por usar la Pokedex! Hasta luego.")
                break

            else:
                print("Opcion invalida")
            Utils.clear()

    def __guardar_partida(self):
        if self.mi_pokemon is None:
            print('Error: no existe pokemon inicial')
            Utils.pause()
            Utils.clear()
            return

        if self.mi_pokemon.pokemon_id is not None:
            self.database.put_pokemon_by_id(self.mi_pokemon)
        for pokemon in self.pokemons_atrapados:
            if pokemon.pokemon_id is not None:
                self.database.put_pokemon_by_id(self.mi_pokemon)
            else:
                self.database.post_pokemon_by_id_user(self.id_jugador, pokemon)

        self.database.put_user_update_by_id(self.id_jugador)

        progreso = self.database.get_user_by_id(self.id_jugador)

        Utils.print_title('Información Guardada para:')
        print(f'Usuario {progreso[1]}')
        print(f'Fecha {progreso[2]}')
        Utils.pause()
        Utils.clear()

    def menu_entrenamiento(self):

        if self.mi_pokemon is None:
            return

        while True:
            Utils.print_title("ENTRENAMIENTO")
            print("1. Entrenamiento Normal")
            print("2. Entrenamiento Individual")
            print("3. Entrenamiento Intensivo")
            print("4. Entrenamiento Personalizado")
            print("0.Volver")
            try:
                op = int(input("Elige una opcion: " ))
            except ValueError:
                print("Ingresa un numero valido.")
                Utils.pause()
                Utils.clear()
                continue

            Utils.clear()
            if op == 1:
                print(f"\nEntrenamiento Normal: actualiza ataque, defensa y nivel (al mismo tiempo)")
                self.mi_pokemon.entrenar()
                self.mi_pokemon.mostrar_datos()
                Utils.pause()
                
            elif op == 2:
                print("1. Subir Ataque")
                print("2. Subir Defensa")
                print("3. Subir Vida")
                try:
                    s = int(input("Elige:  "))
                    if s == 1:
                        self.mi_pokemon.subirAtaque()
                    elif s == 2:
                        self.mi_pokemon.subirDefensa()          
                    elif s == 3:
                        self.mi_pokemon.subirVida()
                    else:
                        print("Opcion invalida.")
                except ValueError:
                    print("Valor invalido.")
                Utils.pause()

            elif op == 3:
                print("\nEntrenamiento Intensivo: actualiza ataque, defensa y vida con boost.")
                self.mi_pokemon.actualizar()
                self.mi_pokemon.mostrar_datos()
                Utils.pause()


            elif op == 4:
                try:
                    a = int(input("Ingresa nuevo valor de Ataque:  "))
                    d = int(input("Ingresa nuevo valor de Defensa:  "))
                    v = int(input("Ingresa nuevo valor de Vida:  "))
                    
                    self.mi_pokemon.ataque += a
                    self.mi_pokemon.defensa += d
                    self.mi_pokemon.vida += v
                    

                    print("Valores actualizados manualmente.")
                except ValueError:
                    print("Entrada invalida.")

                self.mi_pokemon.mostrar_datos()
                Utils.pause()
                
            elif op == 0:
                break
            else: 
                print("Opcion invalida.")
            Utils.clear()

#combate u atrapado

    def select_enemy(self) -> Agua | Fuego | Hierba | Electrico:
        if not self.enemigos:
            self.enemigos = self._crear_enemigos_por_defecto()
        enemy = random.choice(self.enemigos)
        return enemy

    def menu_combatir(self):
        Utils.print_title("COMBATE")
        print("Deseas elegir un enemigo o que sea aleatoreamente?")
        print("1. Aleatorio")
        print("2. Elegir de la lista")
        print("0. Volver")
        try:
            choice = int(input("Elige:  "))
        except ValueError:
            print("Valor invalido.")
            Utils.pause()
            return
        Utils.clear()
        if choice == 0:
            return 
        if choice == 1:
            enemigo = self.select_enemy()
        else:
            for i, e in enumerate(self.enemigos, start = 1):
                print(f"{i}. {e.nombre} - Ataque {e.ataque} | Defensa {e.defensa} | Vida {e.vida} | Nivel {e.nivel}")
            try:
                idx = int(input("Elige indice:  ")) - 1
                enemigo = self.enemigos[idx]
            except Exception:
                print("Seleccion invalida.")
                Utils.pause()
                return
        #combate por turnos
        Utils.clear()
        self.combate_con_enemigo(enemigo)

    def combate_con_enemigo(self, enemigo: Agua | Fuego | Hierba | Electrico):
        if self.mi_pokemon is None:
            return

        mi_def = self.mi_pokemon.defensa
        mi_vida = self.mi_pokemon.vida
        en_def = enemigo.defensa
        en_vida = enemigo.vida
        turno_jugador = True

        while (mi_vida > 0) and (en_vida > 0):
            Utils.print_title("COMBATE - ESTADO ")
            print("Tu Pokemon:  ")
            print(f"{self.mi_pokemon.nombre} | Ataque: {self.mi_pokemon.ataque} | Defensa:{mi_def} | Vida: {mi_vida}")
            print("-" * 40)
            print("Enemigo:  ")
            print(f"{enemigo.nombre} | Ataque: {enemigo.ataque} | Defensa: {en_def} | Vida: {en_vida}")
            print("-" * 40)

            if turno_jugador:
                print("Tu turno: elige una accion")
                print("1. Pasar turno")
                print("2. Ataque normal")
                print("3. Ataque especial")
                print("4. Huir")

                try:
                    op = int(input("Elige:  "))
                except ValueError:
                    print("Entrada invalida, se considera pasar turno.")
                    op = 1

                if op == 1:
                    print("Pase el turno.")

                elif op == 2:
                    en_def, en_vida = aplicar_daño(self.mi_pokemon.ataque, en_def, en_vida)
                    print(f"Hiciste un ataque normal con {self.mi_pokemon.ataque}.")

                    mi_def, mi_vida = aplicar_daño(enemigo.ataque, mi_def, mi_vida)
                    print(f"{enemigo.nombre} te contraataca ({enemigo.ataque}).")

                elif op == 3:
                    atk_val = int(self.mi_pokemon.ataque * 1.5)
                    en_def, en_vida = aplicar_daño(atk_val, en_def, en_vida)
                    special = getattr(self.mi_pokemon, "ataque_especial", "Ataque Especial")
                    print(f"{self.mi_pokemon.nombre} usa {special} ({atk_val} dmg).")

                    mi_def, mi_vida = aplicar_daño(enemigo.ataque, mi_def, mi_vida)
                    print(f"{enemigo.nombre} te contraataca ({enemigo.ataque}).")

                elif op == 4:
                    print("Huyes del combate.")
                    Utils.pause()
                    return
                    
                else:
                    print("Opcion invalida, se considera pasar turno.")
                    
                turno_jugador = False
            else:
                choice = random.choice([1, 2, 3])
                
                if choice == 1:
                    print(f"{enemigo.nombre} pasa el turno.")

                elif choice == 2:
                    mi_def, mi_vida = aplicar_daño(enemigo.ataque, mi_def, mi_vida)
                    print(f" {enemigo.nombre} te golpea con ataque normal ({enemigo.ataque}).")

                elif choice == 3:
                    atk_val = int(enemigo.ataque * 1.5)
                    mi_def, mi_vida = aplicar_daño(atk_val, mi_def, mi_vida)
                    special = getattr(enemigo, "ataque_especial", "Atgaque Especial")
                    print(f"{enemigo.nombre} usa {special} ({atk_val} dmg).")

                turno_jugador = True

            Utils.pause()
            Utils.clear()


        Utils.clear()
        if en_vida <= 0:
            print("Has derrotado al enemigo!")
            if enemigo.vida < self.mi_pokemon.vida:
                print("Puedes elegir atraparlo.")
                print("1. Atrapar")
                print("2. No atrapar")
                try:
                    sel = int(input("Elige: "))
                except ValueError:
                    sel = 2
                if sel == 1:
                    enemigo.atrapado = True
                    self.pokemons_atrapados.append(enemigo)
                    print(f"Has atrapado a {enemigo.nombre}!")
                else:
                    print("Decides no atrapar.")
            else:
                print("El enemigo es demasiado fuerte para atraparlo.")
        else:
            print("Has sido derrotado...")
        Utils.pause()

    def VerPokemonsAtrapados(self):
        Utils.print_title("POKEMON ATRAPADOS")
        if not self.pokemons_atrapados:
            print("No has atrapado pokemons aun. ")
        else:
            for i, p in enumerate(self.pokemons_atrapados, start = 1):
                print(f"{i}. {p.nombre} - Ataque: {p.ataque} Defensa:{p.defensa} Vida:{p.vida} Nivel:{p.nivel}")
        Utils.pause()

    def crear_pokemon_enemigo_manual(self):
        Utils.print_title("CREAR POKEMON ENEMIGO")
        while True:
            try:
                nombre = input("Nombre del enemigo: ").strip() or "Enemigo creado"
                desc = input("Descripcion:  ").strip() or "Enemigo"

                while True:
                    ataque = int(input("Ataque(1-100): "))
                    if ataque > 0 and ataque < 101:
                        break
                    print('Fuera de rango, intente de nuevo')

                while True:
                    defensa = int(input("Defensa (1-100):  "))
                    if defensa > 0 and defensa < 101:
                        break
                    print('Fuera de rango, intente de nuevo')

                while True:
                    vida = int(input("Vida (1-100):  "))
                    if vida > 0 and vida < 101:
                        break
                    print('Fuera de rango, intente de nuevo')

                while True:
                    nivel = int(input("Nivel (1-99):  "))
                    if nivel> 0 and nivel < 100:
                        break
                    print('Fuera de rango, intente de nuevo')

                break
            except ValueError:
                print("Entrada invalida - valores numericos requeridos.")
                Utils.pause()

        print("Tipo del enemigo: ")
        print("1. Agua  2. Fuego  3. Electrico  4. Hierba ")
        while True:
            try:
                t = int(input("Elige tipo: "))
                if t > 4 or t < 1:
                    raise ValueError 
                break
            except ValueError:
                print('Inserte un valor válido')
        if t == 1:
            nuevo = Agua(nombre, desc, ataque, defensa, vida, nivel)
        elif t == 2:
            nuevo = Fuego(nombre, desc, ataque, defensa, vida, nivel)
        elif t == 3:
            nuevo = Electrico(nombre, desc, ataque, defensa, vida, nivel)
        else:
            nuevo = Hierba(nombre, desc, ataque, defensa, vida, nivel)
        self.enemigos.append(nuevo)
        print(f"Enemigo {nuevo.nombre} creado y añadido a la lista de enemigos. ")
        Utils.pause()


    def pruebas_manejo_errores(self):
        while True:
            opt = -1
            while True:
                Utils.print_title( "PRUEBAS DE MANEJO DE ERRORES ")
                print("Estas son las pruebas controladas y muestran manejo de excepciones.")
                print("1. ValueError")
                print("2. IndexError")
                print("3. ZeroDivisionError")
                print("4. FileNotError")
                print("5. IOError")
                print("0. Volver")
                try:
                    opt = int(input("Elige pruebas: "))
                    if opt < 0 or opt > 5:
                        raise ValueError
                    break
                except ValueError:
                    print('Seleccione una opción valida')

            if opt == 1:
                try:
                    x = int("No es numero")
                except ValueError as e:
                    print("Se capturo ValueError: ", e)

                Utils.pause()
                Utils.clear()
            elif opt == 2:
                try:
                    a = [1, 2, 3]
                    print(a[10])
                except IndexError as e:
                    print("Se capturo IndexError: ", e)

                Utils.pause()
                Utils.clear()
            elif opt == 3:
                try:
                    x = 1 / 0
                except ZeroDivisionError as e:
                    print("Se capturo ZeroDivisionError: ", e)

                Utils.pause()
                Utils.clear()
            elif opt == 4:
                try:
                    with open("archivo_que_no_existe.txt", "r") as f:
                        _ =f.read()
                except FileNotFoundError as e:
                    print("Se capturo FileNotFoundError: ", e)

                Utils.pause()
                Utils.clear()
            elif opt == 5:
                try:
                    with open("/invalid_path/test.txt", "w") as f:
                        f.write("prueba")
                except IOError as e:
                    print("Se capturo IOError: ", e)
                except Exception as e:
                    print("Se capturo otra excepcion: ", e)

                Utils.pause()
                Utils.clear()
            else:
                print("Volviendo al menu.")
                Utils.pause()
                Utils.clear()
                break
        
if __name__ == "__main__":
    try:
        App()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.  Hasta luego! ")
