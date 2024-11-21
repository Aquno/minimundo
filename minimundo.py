import os
import xml.etree.ElementTree as ET
from collections import deque
import datetime

# Caminhos dos arquivos XML
ARQUIVO_PACIENTES = "pacientes.xml"
ARQUIVO_ATENDIMENTOS = "atendimentos.xml"

# Inicialização dos arquivos XML
def inicializar_arquivos():
    if not os.path.exists(ARQUIVO_PACIENTES):
        root = ET.Element("pacientes")
        tree = ET.ElementTree(root)
        tree.write(ARQUIVO_PACIENTES)
    
    if not os.path.exists(ARQUIVO_ATENDIMENTOS):
        root = ET.Element("atendimentos")
        tree = ET.ElementTree(root)
        tree.write(ARQUIVO_ATENDIMENTOS)

# Funções auxiliares para manipulação de XML
def carregar_pacientes():
    tree = ET.parse(ARQUIVO_PACIENTES)
    root = tree.getroot()
    pacientes = {}
    for paciente in root.findall("paciente"):
        cpf = paciente.find("CPF").text
        pacientes[cpf] = {
            "CPF": cpf,
            "Nome": paciente.find("Nome").text,
            "Data de Nascimento": paciente.find("DataNascimento").text,
            "Endereço": paciente.find("Endereco").text,
            "Telefones": paciente.find("Telefones").text.split(','),
            "Histórico": []
        }
    return pacientes

def salvar_paciente(paciente):
    tree = ET.parse(ARQUIVO_PACIENTES)
    root = tree.getroot()
    
    paciente_elem = ET.Element("paciente")
    ET.SubElement(paciente_elem, "CPF").text = paciente["CPF"]
    ET.SubElement(paciente_elem, "Nome").text = paciente["Nome"]
    ET.SubElement(paciente_elem, "DataNascimento").text = paciente["Data de Nascimento"]
    ET.SubElement(paciente_elem, "Endereco").text = paciente["Endereço"]
    ET.SubElement(paciente_elem, "Telefones").text = ','.join(paciente["Telefones"])
    
    root.append(paciente_elem)
    tree.write(ARQUIVO_PACIENTES)

def salvar_atendimento(atendimento):
    tree = ET.parse(ARQUIVO_ATENDIMENTOS)
    root = tree.getroot()
    
    atendimento_elem = ET.Element("atendimento")
    ET.SubElement(atendimento_elem, "PacienteCPF").text = atendimento["Paciente"]["CPF"]
    ET.SubElement(atendimento_elem, "Data").text = atendimento["Data"]
    ET.SubElement(atendimento_elem, "Motivo").text = atendimento["Motivo"]
    ET.SubElement(atendimento_elem, "Diagnóstico").text = atendimento.get("Diagnóstico", "")
    ET.SubElement(atendimento_elem, "Receita").text = atendimento.get("Receita", "")
    ET.SubElement(atendimento_elem, "Retorno").text = atendimento.get("Retorno", "")
    
    root.append(atendimento_elem)
    tree.write(ARQUIVO_ATENDIMENTOS)

# Estruturas de dados
pacientes = carregar_pacientes()
fila_espera = deque()
senha_atual = 0

# Funções principais
def criar_ficha_paciente():
    cpf = input("Digite o CPF do paciente: ")
    if cpf in pacientes:
        print("Paciente já cadastrado.")
        return pacientes[cpf]
    
    nome = input("Digite o nome do paciente: ")
    data_nasc = input("Digite a data de nascimento (dd/mm/yyyy): ")
    endereco = input("Digite o endereço: ")
    telefones = input("Digite os telefones (separe por vírgulas): ").split(',')
    
    paciente = {
        "CPF": cpf,
        "Nome": nome,
        "Data de Nascimento": data_nasc,
        "Endereço": endereco,
        "Telefones": telefones,
        "Histórico": []
    }
    pacientes[cpf] = paciente
    salvar_paciente(paciente)
    print("Paciente cadastrado com sucesso!")
    return paciente

def atender_paciente():
    global senha_atual
    if not fila_espera:
        print("Nenhum paciente na fila.")
        return

    senha = fila_espera.popleft()
    print(f"Chamando paciente da senha {senha}")
    
    cpf = input("Digite o CPF do paciente: ")
    if cpf not in pacientes:
        print("Paciente não encontrado. Realizando cadastro...")
        paciente = criar_ficha_paciente()
    else:
        paciente = pacientes[cpf]
    
    motivo = input("Qual o motivo da consulta? (Consulta de rotina/Dor de dente): ")
    ficha_atendimento = {
        "Paciente": paciente,
        "Motivo": motivo,
        "Data": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    salvar_atendimento(ficha_atendimento)
    print("Paciente registrado para atendimento. Aguarde ser chamado pelo dentista.")

def chamar_dentista():
    tree = ET.parse(ARQUIVO_ATENDIMENTOS)
    root = tree.getroot()
    
    if len(root) == 0:
        print("Nenhum paciente para atendimento.")
        return

    atendimento_elem = root[0]
    paciente_cpf = atendimento_elem.find("PacienteCPF").text
    paciente = pacientes.get(paciente_cpf, {"Nome": "Desconhecido"})
    
    print(f"Chamando paciente: {paciente['Nome']}")
    print(f"Motivo da consulta: {atendimento_elem.find('Motivo').text}")
    
    diagnostico = input("Descreva o diagnóstico: ")
    receita = input("Digite a receita, se houver: ")
    retorno = input("Solicitar retorno? (Sim/Não): ")
    
    atendimento_elem.find("Diagnóstico").text = diagnostico
    atendimento_elem.find("Receita").text = receita
    atendimento_elem.find("Retorno").text = retorno
    tree.write(ARQUIVO_ATENDIMENTOS)
    
    print("Consulta finalizada. Paciente liberado.")

def gerar_senha():
    global senha_atual
    senha_atual += 1
    fila_espera.append(senha_atual)
    print(f"Sua senha é: {senha_atual}")

# Menu principal
def menu():
    inicializar_arquivos()
    while True:
        print("\n--- Consultório Dentibão ---")
        print("1. Gerar senha")
        print("2. Atender paciente (Recepção)")
        print("3. Chamar paciente (Dentista)")
        print("4. Sair")
        
        opcao = input("Escolha uma opção: ")
        if opcao == "1":
            gerar_senha()
        elif opcao == "2":
            atender_paciente()
        elif opcao == "3":
            chamar_dentista()
        elif opcao == "4":
            print("Encerrando o sistema. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Iniciar o programa
menu()
