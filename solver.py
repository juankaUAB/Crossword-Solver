import numpy as np
import copy as cp
import time
import typing

class Word: #classe per a guardar l'informació sobre les variables del tauler
    def __init__(self, coord: tuple, length: int, list_cells: list):
        self.length = length
        self.list_cells = list_cells
        self.list_inters = []
    
        
class Board: #classe per a guardar l'informació sobre el tauler
    def __init__(self, filename: str):
        self.board = self.read_board(filename)
        self.n_cols = self.board.shape[1]
        self.n_rows = self.board.shape[0]
        self.list_words = []
        self.list_len = []
        
        if self.board.size != 0:     #comprovacio tauler buit
            self.analize_board()
        else:
            print("Tauler buit; no es poden crear les variables")
        self.find_intersections()
    
    def read_board(self, filename: str): #funcio de la classe Board, lleguim el .txt i ho guardem
        crucigrama = np.loadtxt(filename, dtype=str, delimiter='	',comments='-')
        return crucigrama
    
    def analize_board(self): #funcio de la classe Board, analitzem el tauler i iniciem les variables Word
        fil = 0
        for linia in self.board:
            i = 0
            while (i < self.n_cols - 1):
                if (linia[i] == '0' and linia[i+1] == '0'):
                    #vol dir que existeix un lloc per una paraula HORITZONTAL aixi que la creem
                    coord = [fil, i]
                    length = 0
                    list_cells = []
                    while (linia[i] != '#' and i < self.n_cols - 1):
                        list_cells.append([fil,i])
                        length += 1
                        i += 1
                    if (linia[i] == '0'):  #comprovar ultima posicio
                        list_cells.append([fil,i])
                        length += 1
                        i += 1
                    
                    if (length not in self.list_len):
                        self.list_len.append(length)
                    
                    self.list_words.append(Word(coord, length, list_cells))
                else:
                    i += 1
            fil += 1
        #######################################################################################
        col = 0
        while (col < self.n_cols):
            columna = self.board[:,col]
            i = 0
            while (i < self.n_rows - 1):
                if (columna[i] == '0' and columna[i+1] == '0'):
                    #vol dir que existeix un lloc per una paraula VERTICAL aixi que la creem
                    coord = [i, col]
                    length = 0
                    list_cells = []
                    while (columna[i] != '#' and i < self.n_rows - 1):
                        list_cells.append([i,col])
                        length += 1
                        i += 1
                    if (columna[i] == '0'): #comprovar ultima posicio
                        list_cells.append([i,col])
                        length += 1
                        i += 1
                        
                    if (length not in self.list_len):
                        self.list_len.append(length)
                    
                    self.list_words.append(Word(coord, length, list_cells))
                else:
                    i += 1
            col += 1
            
    def find_intersections(self): #funcio de la classe Board, guardem en cada variable Word les altres paraules amb les que intersecta
        word = 0
        total = len(self.list_words)
        while word < total:
            word2 = word + 1
            while word2 < total: #comparem cada parella de paraules i busquem la posició que es troba en les dues llistes (la intersecció)
                llista = [w for w in self.list_words[word].list_cells if w in self.list_words[word2].list_cells]
                for element in llista:
                    self.list_words[word].list_inters.append(self.list_words[word2])
                    self.list_words[word2].list_inters.append(self.list_words[word])
                word2 = word2 + 1
            word = word + 1

    def backtracking(self, assigned_list: list, non_assigned_list: list, dictionary: np.array) -> list: #funcio de la classe Board on implementem el bactracking amb forward-checking
        if len(non_assigned_list) == 0:
            return assigned_list
    
        next_variable = non_assigned_list[0]
        for word in dictionary:
            assigned_list[next_variable] = word
            if self.check_restrictions([next_variable, word], assigned_list) and self.comprovar([next_variable, word], dictionary): #comprovem que es satisfan les restriccions i intentem evitar errors amb aquesta assignacio en un futur
                resultat = self.backtracking(cp.deepcopy(assigned_list), cp.deepcopy(non_assigned_list[1:]), dictionary)
                if len(resultat) == len(self.list_words):
                    return resultat
        
        return []
    
    def comprovar(self, candidate, dictionary): #funcio de la classe Board que utilitzem com a forward-checking (utilitzada en la funció bactracking)
        '''
        FUNCIONAMENT:
        Comprovem si al posar la paraula candidata del diccionari a la posició del taulell, existirien altres paraules al diccionari amb les
        que seria possible l'intersecció. Si no n'existeix cap, descatarem el canvi ja que ens farà tirar enrere.
        Exemple: si volem posar PALMERA i tenim una paraula que comença a la tercera posició, si no hi ha cap paraula que comenci per L no posarem PALMERA
        '''
    
        for interseccio in candidate[0].list_inters:
            possible = False
            valides = [ x for x in dictionary if len(x) == interseccio.length ]
            i = 0
            while i < candidate[0].length and not possible:
                if (candidate[0].list_cells[i] in interseccio.list_cells):
                    intersect_pos = interseccio.list_cells.index(candidate[0].list_cells[i])
                    for paraula in valides:
                        if (candidate[1][i] == paraula[intersect_pos]):
                            possible = True
                            break
                i += 1
            if not possible:
                return False
        return True
                    
    def check_restrictions(self, candidate: tuple, assigned_list: list) -> bool: #funcio de la classe Board, revisa que es compleixin les restriccions (utilitzada en la funció bactracking)
        if (len(candidate[1]) == candidate[0].length): #Primera condició: que la paraula candidata tingui la mateixa longitud que la paraula buida
            list_inter = []
            for paraula in candidate[0].list_inters:
                for casella in paraula.list_cells:
                    if casella in candidate[0].list_cells:
                        pos = candidate[0].list_cells.index(casella)
                        list_inter.append(candidate[0].list_cells[pos])
                        break
            
            if len(list_inter) == 0:
                return True
            for aword in assigned_list.keys():
                if aword == candidate[0]:
                    continue
                elif candidate[1] == assigned_list[aword]: #Segona condició: que la paraula candidata ja no estigui assignada (no es poden repetir les paraules al tauler)
                    return False
                    
            else:
                list_wordsThatIntersect = []
                for inters in list_inter: #En aquest bucle agafem totes les paraules que intersecten amb la candidata
                    for word in assigned_list.keys():
                        if inters in word.list_cells and candidate[0] != word:
                            list_wordsThatIntersect.append(word)
                for i, word in enumerate(list_wordsThatIntersect):
                    assign = word.list_cells.index(list_inter[i]) #El metode index ens agafarà la posició de la lletra que intersecta
                    candi = candidate[0].list_cells.index(list_inter[i])
                    if candidate[1][candi] != assigned_list[word][assign]: #Tercera condició: que la intersecció entre dues paraules tingui la mateixa lletra
                        return False
                return True
        return False
    
    def fill_board(self, assigned_variables: list): #funcio de la classe Board per a omplir el tauler
        for i in zip(assigned_variables.keys(), assigned_variables.values()):
            for w in zip(i[0].list_cells, i[1]):
                x = w[0][0]
                y = w[0][1]
                self.board[x][y] = w[1]
                
    def print_board(self): #funcio de la classe Board per a dibuixar el tauler a la consola
        for row in self.board:
            print("+---+---+---+---+---+---+")
            for i,column in enumerate(row):
                print("|", column, end=" ")
                if i == len(row) - 1:
                    print("|", end="")
            print()
        print("+---+---+---+---+---+---+")
        
    
def read_dictionary(filename: str, board) -> np.array: #funcio on llegim el diccionari, directament descartem les paraules que tenen una longitud que no existeix al taulell
    
    diccionari = np.array([word for word in open(filename).read().splitlines() if len(word) in board.list_len])
    return diccionari
   
      

def main():
    board = Board("crossword_CB_v2.txt")
    dictionary = read_dictionary("diccionari_CB_v2.txt", board)
    inici = time.time()
    assigned_variables = board.backtracking(dict(), cp.deepcopy(board.list_words), dictionary)
    final = time.time()
    board.fill_board(assigned_variables)
    print("Time elapsed: ",final - inici)
    board.print_board()


if __name__ == "__main__":
    main()