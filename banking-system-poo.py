import textwrap
from abc import ABC, abstractclassmethod, abstractproperty
from datetime import datetime

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = [] # declarando a lista de contas
        
    def realizar_transacao(self, conta, transacao):
        transacao.registar(conta)
    
    #  Método para adicionar a conta na lista de contas
    def adicionar_conta(self, conta):
        self.contas.append(conta)

# Classe PessoaFisica extende da classe Cliente obtendo apenas a instância endereço
class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco) # Pegando da classe Cliente
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf
        
    # Foram herdados os 2 métodos da classe cliente

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
    
    # Método para criar uma nova conta
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente) # Retorna uma instância de conta
    
    # Getters dos variáveis instanciadas
    @property
    def saldo(self):
        return self._saldo
        
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self.cliente

    @property
    def historico(self):
        return self._historico
    
    # Métodos da classe Conta
    
    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo # Variável indicando se a quantia a sacar vai exceder o saldo ou não. True ou False
        
        if excedeu_saldo: # Se a quantia à sacar for maior que seu saldo vai printar essa mensagem de erro 
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            
        elif valor > 0: # Se não excedeu o saldo e o valor inserido é váliddo ele vai sacar
            self._saldo -= valor # Tirando o valor da conta
            print("\n=== Saque foi realizado com sucesso! ===")
            return True # Identificando que a operação realizada deu certo
            
        else:
            print("\n@@@ Operação falhou! O valor informado é inválido! @@@")
            
        return False # Se não retornar True indicando que foi sacado, vai retornar False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n=== O valor foi depositado com sucesso! ===")
        else: 
            print("\n@@@ Operação falhou! O valor informado é inválido! @@@")
            return False # Se a operaçãO falhar ela vai soltar o False
        
        return True # Se não falhar ele vai soltar o True

class ContaCorrente(Conta): # Classe ContaCorrente vai herdar a Conta
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite 
        self.limite_saques = limite_saques
    
    # Sobrepondo a def de saque da classe pai, pois nessa classe ele deve fazer algumas validações 
    def sacar(self, valor):
        
        numero_saques = len([transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]) # Verificando nos histórico se ele já sacou 3 vezes
        
        excedeu_limite = valor > self.limite # Se excedeu o limite de 500 reais da conta
        excedeu_saques = numero_saques >= self.limite_saques # Usando essa variável para verificar se ele excedeu o limite de 3 saques
        
        if excedeu_limite:
            print("\n@@@ Operação falhou! Você excedeu o limite de saque @@@")
            
        elif excedeu_saques:
            print("\n @@@ Operação falhou! Você excedeu o limite de 3 saques. @@@")
        
        else:
            return super().sacar(valor) # Essa operação já retorna True
        
        return False
    
    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
            """

class Historico:
    def __init__(self):
        self._transacoes = []
    
    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
             "tipo": transacao._class__.__name__,   
             "valor": transacao.valor,
             "data": datetime.now().strftime
             ("%d-%m-%Y %H:%M:%s"),
            }
        )
        
class Transacao(ABC): # Criando uma interface/classe abstrata
    @property
    @abstractproperty
    def valor(self):
        pass
    
    @abstractclassmethod
    def registrar(self, valor):
        pass
    
class Saque(Transacao): # Herdando a interface
    def __init__(self, valor):
        self._valor = valor
        
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)
        
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
            
class Deposito(Transacao): # Herdando a interface
    def __init__(self, valor):
        self._valor = valor
        
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)
        
        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)
            
# Funções para funcionar o sistema

def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\n@@@ Cliente não possui conta! @@@")
        return

    # FIXME: não permite cliente escolher a conta
    return cliente.contas[0]


def depositar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do depósito: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    valor = float(input("Informe o valor do saque: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(clientes):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado! @@@")
        return

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n================ EXTRATO ================")
    transacoes = conta.historico.transacoes

    extrato = ""
    if not transacoes:
        extrato = "Não foram realizadas movimentações."
    else:
        for transacao in transacoes:
            extrato += f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}"

    print(extrato)
    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("==========================================")


def criar_cliente(clientes):
    cpf = input("Informe o CPF (somente número): ")
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)

    clientes.append(cliente)

    print("\n=== Cliente criado com sucesso! ===")


def criar_conta(numero_conta, clientes, contas):
    cpf = input("Informe o CPF do cliente: ")
    cliente = filtrar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Cliente não encontrado, fluxo de criação de conta encerrado! @@@")
        return

    conta = ContaCorrente.nova_conta(cliente=cliente, numero=numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n=== Conta criada com sucesso! ===")


def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(textwrap.dedent(str(conta)))


def main():
    clientes = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(clientes)

        elif opcao == "s":
            sacar(clientes)

        elif opcao == "e":
            exibir_extrato(clientes)

        elif opcao == "nu":
            criar_cliente(clientes)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, clientes, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")


main()