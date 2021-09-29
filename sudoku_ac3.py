# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 10:59:58 2020

@author: alexa
"""

import itertools
import time


rows = "123456789"
cols = "ABCDEFGHI"


def AC3(csp, queue=None):
    if queue is None:
        queue = list(csp.binary_constraints)

    while queue:
        (xi, xj) = queue.pop(0)

        if remove_inconsistent_values(csp, xi, xj):
            # se uma das células tiver 0 possibilidades o sudoku não tem solução
            if len(csp.possibilities[xi]) == 0:
                return False

            for Xk in csp.related_cells[xi]:
                if Xk != xi:
                    queue.append((Xk, xi))
    return True


def remove_inconsistent_values(csp, cell_i, cell_j):
    removed = False  # se o dominio nunca for reduzido é sempre devolvido false

    # percorre cada valor possível restante para a cell_i
    for value in csp.possibilities[cell_i]:

        # se cell_i=value estiver em conflito com cell_j=poss
        if not any([is_different(value, poss) for poss in csp.possibilities[cell_j]]):
            # então remove cell_i=value do dominio
            csp.possibilities[cell_i].remove(value)
            removed = True

    return removed  # devolve true se algum valor tiver sido eliminado


# is_different: verifica se 2 células são diferentes
def is_different(cell_i, cell_j):
    result = cell_i != cell_j
    return result


class Sudoku:

    """
    INICIALIZAÇÃO
    """
    def __init__(self, grid):
        game = list(grid)
        
        # criação de todas as células das grelhas
        self.cells = list()
        self.cells = self.generate_coords()

        # criação de todas as possibilidades para cada uma dessas células
        self.possibilities = dict()
        self.possibilities = self.generate_possibilities(grid)
   
        # criação das restrições linha/coluna /quadrado
        rule_constraints = self.generate_rules_constraints()

        # conversão dessas restrições para restrições binárias
        self.binary_constraints = list()
        self.binary_constraints = self.generate_binary_constraints(rule_constraints)

        # cria todas as restrições relacionadas com cada uma das células
        self.related_cells = dict()
        self.related_cells = self.generate_related_cells()

        #prune(poda)
        self.pruned = dict()
        self.pruned = {v: list() if grid[i] == '0' else [int(grid[i])] for i, v in enumerate(self.cells)}


    """
    gera todas as coordenadas das células
    """
    def generate_coords(self):

        all_cells_coords = []

        #  A,B,C, ... ,H,I
        for col in cols:

            #1,2,3 ,... ,8,9
            for row in rows:
                
                # A1, A2, A3, ... , H8, H9
                new_coords = col + row
                all_cells_coords.append(new_coords)

        return all_cells_coords

    """
    gera todos os valores possíveis restantes para cada célula
    """
    def generate_possibilities(self, grid):

        grid_as_list = list(grid)

        possibilities = dict()

        for index, coords in enumerate(self.cells):
            # se o valor for 0, então a célula pode ter qualquer valor entre [1, 9].
            if grid_as_list[index] == "0":
                possibilities[coords] = list(range(1,10))
            # caso contrário, o valor já está definido, as possibilidades são esse valor.
            else:
                possibilities[coords] = [int(grid_as_list[index])]

        return possibilities

    """
    gera as restrições baseadas nas regras deste jogo:
     valor diferente de qualquer outro na mesma linha, coluna ou grelha
    """
    def generate_rules_constraints(self):
        
        row_constraints = []
        column_constraints = []
        square_constraints = []

        # obtem se as restrições das filas
        for row in rows:
            row_constraints.append([col + row for col in cols])

        # obtem se as restrições das colunas
        for col in cols:
            column_constraints.append([col + row for row in rows])

        # obtem se as restrições das grelhas
        # https://stackoverflow.com/questions/9475241/split-string-every-nth-character
        rows_square_coords = (cols[i:i+3] for i in range(0, len(rows), 3))
        rows_square_coords = list(rows_square_coords)

        cols_square_coords = (rows[i:i+3] for i in range(0, len(cols), 3))
        cols_square_coords = list(cols_square_coords)

        # percorre cada grelha
        for row in rows_square_coords:
            for col in cols_square_coords:

                current_square_constraints = []
                
                # e para cada valor nesta grelha
                for x in row:
                    for y in col:
                        current_square_constraints.append(x + y)

                square_constraints.append(current_square_constraints)

        # todas as restriçõs são a soma destas 3 regras
        return row_constraints + column_constraints + square_constraints

    """
    gera as restrições binárias com base nas regras de restrição
    """
    def generate_binary_constraints(self, rule_constraints):
        generated_binary_constraints = list()

        # percorre cada conjunto de restrições
        for constraint_set in rule_constraints:

            binary_constraints = list()

            # 2 porque queremos restrições binárias
            # solução retirada em :
            # https://stackoverflow.com/questions/464864/how-to-get-all-possible-combinations-of-a-list-s-elements
            

            for tuple_of_constraint in itertools.permutations(constraint_set, 2):
                binary_constraints.append(tuple_of_constraint)

            # percorre cada uma destas restriçoes binárias
            for constraint in binary_constraints:

                # verifica se já temos esta restrição guardada
                # solution from https://stackoverflow.com/questions/7571635/fastest-way-to-check-if-a-value-exist-in-a-list
                constraint_as_list = list(constraint)
                if(constraint_as_list not in generated_binary_constraints):
                    generated_binary_constraints.append([constraint[0], constraint[1]])

        return generated_binary_constraints

    """
    gera a célula relacionada com cada uma das restições
    """
    def generate_related_cells(self):
        related_cells = dict()

        #percorre cada uma das 81 celulas
        for cell in self.cells:

            related_cells[cell] = list() # related_cells são aquelas com quem a célula atual tem restrições

            for constraint in self.binary_constraints:
                if cell == constraint[0]:
                    related_cells[cell].append(constraint[1])

        return related_cells

    """
    verifica se a solução do Sudoku está pronta
    fazemos um loop através das possibilidades de cada célula
    se todos eles tiverem apenas um, então o Sudoku está resolvido
    """
    def isFinished(self):
        for coords, possibilities in self.possibilities.items():
            if len(possibilities) > 1:
                return False
        
        return True
    
    """
    devolve uma string legível por humanos
    """
    def __str__(self):

        output = ""
        count = 1
        
        # percorre cada célula e imprime o seu valor
        for cell in self.cells:


            value = str(self.possibilities[cell])
            if type(self.possibilities[cell]) == list:
                value = str(self.possibilities[cell][0])

            output += "[" + value + "]"

            # se chegarmos ao fim da linha passa para uma nova linha
            if count >= 9:
                count = 0
                output += "\n"
            
            count += 1
        
        return output

exemplo = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'


def solve(grid, index, total):
    print("\nSudoku {}/{} : \n{}".format(index, total, print_grid(grid)))
    print("{}/{} : AC3 iniciou".format(index, total))

    tic = time.perf_counter()

    # instancia Sudoku
    sudoku = Sudoku(grid)

    # arranca o algoritmo AC-3
    AC3_result = AC3(sudoku)
    print(AC3_result)

    toc = time.perf_counter()

    timeFinal = toc - tic

    print("{}/{} : Resultado: \n{}".format(index, total, sudoku))
    print(f"\nTempo de cálculo: {toc - tic:0.4f}s\n")

    return timeFinal

def print_grid(grid):

    output = ""
    count = 1

    # percorre cada célula e imprime o seu valor
    for cell in grid:

        value = cell
        output += "[" + value + "]"

        #  se chegarmos ao fim da linha,
        # cria uma nova linha no display
        if count >= 9:
            count = 0
            output += "\n"

        count += 1

    return output

#Função para executar o algoritmo x vezes
#Permite fazer uma averiguação de custo de tempo
def cicloTeste(iter):
    total = 0
    for i in range(iter):
        print("Iteração: " + str(i))
        total += solve(exemplo, 0, 1)
    tempoFinal = total/iter
    print("Média do tempo de cálculo após " + str(iter) + " iterações: " + str(tempoFinal))

#Função simples para user input
def inputUser():
    val = input("Introduza o número de vezes que pretende executar este algoritmo? \n")
    cicloTeste(int(val))

#Duas opções para executar
#Executa apenas uma vez:
solve(exemplo, 0, 1)

#executa X vezes (ou 10 em debugging)
#cicloTeste(10)
#inputUser()