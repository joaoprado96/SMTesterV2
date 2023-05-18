import sys
import asyncio
import codecs
import time
import threading
import json

# Receber o argumento enviado do Node.js
arg_from_node = sys.argv[1]

# String JSON
json_string = sys.argv[1]

# Converte a string em dicionário Python
data = json.loads(json_string)

# Acessando os elementos
print(data["dropdownValues"][0])  # Imprime 'John'
monitor=data["dropdownValues"][0]
porta=data["dropdownValues"][1]
num_conexoes=int(data["dropdownValues"][2])
timeout=10
latencia=10
qtd_exec=data["dropdownValues"][0]
qtdterm=data["dropdownValues"][0]
transacao=data["dropdownValues"][0]
saved_text=data["dropdownValues"][0]

# Utilizar o argumento na lógica do script Python
print(f"Argumento recebido do Node.js: {arg_from_node}")

class Conexao:
    timeout     = 15
    latencia    = 0
    monitores   = { 'LOCALHOST':'127.0.0.1',
                    'TESTER1': '172.23.34.173',
                    'TESTFI1': '172.23.34.174',
                    'TESTER2': '172.23.34.217',
                    'TESTM26': '172.23.35.76',
                    'TESTM26': '172.23.35.76',
                    'TESTM27': '172.23.35.77'
                  }
    agencias    = { 'LOCALHOST':'9999',
                    'TESTER1': '1500',
                    'TESTFI1': '2000',
                    'TESTER2': '172.23.34.217',
                    'TESTM26': '0260',
                    'TESTM26': '172.23.35.76',
                    'TESTM27': '172.23.35.77'
                  }
    
    def __init__(self,monitor,porta,nome,timeout,latencia):
        self.IP = Conexao.monitores[monitor]
        self.porta = porta
        self.nome = nome
        self.monitor = monitor
        self.agencia = Conexao.agencias[monitor]
        self.timeout = timeout
        self.latencia = latencia
        self.logico = Conexao.agencias[monitor]
        self.serie = '00000'
        self.hexa = '0000'
    
    async def cria_comando_m(self):
        return ('2000M00000000000000000000000000000000000000000S'+self.nome)

    def cria_comando_M_canal(self,terminal,enviado):
        return ('2000M9999710100004341'+self.agencia+'000000000000'+terminal+'004341'+self.agencia+self.logico)    
    
    def cria_transacao_qt(self,hexa,xml,token,nrcon):
        return ('4000A0001004341'+self.agencia+'QT 710'+format(nrcon, '02')+str(hexa)+'01QTIF1'+xml+token)
    
    #Função para abertura de uma conexão TCP/IP
    async def conecta(self):
        try:
            self.reader,self.writer = await asyncio.wait_for(asyncio.open_connection(self.IP,self.porta),timeout=Conexao.timeout)
        except:
            raise
    
    #Função para encerramento de uma conexão TCP/IP
    async def encerra_conexao(self):
        try:
            self.writer.close()
            await self.writer.wait_closed()
        except:
            raise

    #Função para enviar uma mensagem em "cp500"
    async def envia_mensagem(self, message):
        try:
            self.hexa = message[26:31]
            tammsg = len(message)
            bytestammsg = tammsg.to_bytes(4,byteorder="big")
            bytemsg = codecs.encode(message,'cp500')
            mensagem = bytestammsg + bytemsg
            self.writer.write(mensagem)
            await self.writer.drain()
            time.sleep(self.latencia/1000) #Tempo ente mensagens

        except:
            raise
    

    #Função para receber o comando M
    async def recebe_comando_M(self):
        try:
            bytestammsg = await asyncio.wait_for(self.reader.read(4), timeout = Conexao.timeout)
            tamanho = int.from_bytes(bytestammsg, byteorder="big")
            bytestammsg = await self.reader.read(tamanho)
            bytestammsg = await asyncio.wait_for(self.reader.read(4), timeout = Conexao.timeout)
            tamanho = int.from_bytes(bytestammsg, byteorder="big")
            bytestammsg = await asyncio.wait_for(self.reader.read(tamanho), timeout = Conexao.timeout)
            msgretorno = codecs.decode(bytestammsg, 'cp500')
            return msgretorno
        except:
            raise

    async def recebe_resposta(self):
        try:
            bytestammsg = await asyncio.wait_for(self.reader.read(4), timeout = Conexao.timeout)
            tamanho = int.from_bytes(bytestammsg, byteorder="big")
            bytestammsg = await asyncio.wait_for(self.reader.read(tamanho), timeout = Conexao.timeout)
            msgretorno = codecs.decode(bytestammsg, 'cp500')
            return msgretorno
        except:
            raise

    #Função para enviar uma mensagem em "cp500"
    async def envia_e_recebe(self, message):
        try:
            self.hexa = message[26:31]
            tammsg = len(message)
            bytestammsg = tammsg.to_bytes(4,byteorder="big")
            bytemsg = codecs.encode(message,'cp500')
            mensagem = bytestammsg + bytemsg
            self.writer.write(mensagem)
            await self.writer.drain()
            bytestammsg = await asyncio.wait_for(self.reader.read(4), timeout = Conexao.timeout)
            tamanho = int.from_bytes(bytestammsg, byteorder="big")
            bytestammsg = await asyncio.wait_for(self.reader.read(tamanho), timeout = Conexao.timeout)
            msgretorno = codecs.decode(bytestammsg, 'cp500')
            time.sleep(self.latencia/1000) #Tempo ente mensagens
            
        except:
            raise

async def loop_mensagens(monitor,porta,num_conexoes,timeout,latencia,  qtd_exec, qtdterm, transacao, saved_text):
    global conexoes
    # Criando instâncias de conexões
    conexoes = [Conexao(monitor,porta,"SMTESTER0",timeout,latencia) for _ in range(num_conexoes)]
    
    # Abrindo conexões com o monitor
    await asyncio.gather(*(conexao.conecta() for conexao in conexoes))
    
    #Definindo as listas de terminais com base na quantidade de conexões
    qtd_listas= int(num_conexoes)
    
    #Obtendo a quantidade de terminais por conexão
    qtd_terminais = int(qtdterm)
    
    #Criando as listas de terminais com base na quantidade de coexões
    terminais = [[f"8{j+1:02}{i+1:02}" for i in range(qtd_terminais)] for j in range(qtd_listas)]
    
    print(terminais)
    #Definindo as listas para realização de comandos M
    comandosm=[]

    # Faz os comandos M para cada lista de terminal, utilizando sua respectiva conexão
    for i in range(qtd_listas): #qtd_listas = número de conexões
        comandosm_lista=[]
        for terminal in terminais[i]:  
            comandosm_lista.append(conexoes[i].cria_comando_M_canal(terminal))     
        comandosm.append(comandosm_lista)
    
    #comandosm é uma lista, composta por qtd_listas de comandos M (0....9)
    #Resposta tokens é uma lista unica com todas as respostas dos comandos M devolvidas para os monitores
    #Essa parte é feita de maneira sincrona, para conseguirmos ter todos os tokens em ordem.
    resp_com_tokens=[]
    tokens=[]
    for j, comando in enumerate(comandosm):
        for i, m in enumerate(comando):
            await conexoes[j].envia_mensagem(m)
            resp_com_tokens.append(await conexoes[j].recebe_resposta())

    #Tranformar as respostas em token, ou seja extrai o TOKEN do comando 5000O
    for token in resp_com_tokens:
        substring=token[9:59]
        tokens.append(substring)
        
    # Construir um dicionário dos terminais com os tokens
    terminais_unicos = [terminal for lista in terminais for terminal in lista]
    dicionario_tokens = dict(zip(terminais_unicos, tokens))
    
    #Definindo um hexadecimal para as requisções
    # max_value = 16 ** 4 - 1 # 65.535 (0xFFFF em hexadecimal).
    max_value = int(qtd_exec.get())
    if (transacao == "INPUT"):
        xml = saved_text.get()
    else:
        xml = transacao
    
    # Envia transações simultaneamente por todas as conexões. Para 8 conexões (enviaremos 8 mensagens)
    for j in range(max_value):
        hex_value = format(j, f"0{4}X")
        asyncio.gather(*(conexao.envia_e_recebe(conexao.cria_transacao_qt(hex_value,xml,dicionario_tokens[terminais[i][j % qtd_terminais]],i),enviado,recebido) for i, conexao in enumerate(conexoes)))

    await asyncio.gather(*(conexao.encerra_conexao() for conexao in conexoes))
    return

def run_loop_mensagens_thread(monitor, porta, num_conexoes, timeout, latencia,  qtd_exec, qtdterm, transacao, saved_text):
    asyncio.run(loop_mensagens(monitor, porta, num_conexoes, timeout, latencia,  qtd_exec, qtdterm, transacao, saved_text))

def loop_thread(monitor, porta, num_conexoes, timeout, latencia,  qtd_exec, qtdterm, transacao, saved_text):
    threading.Thread(target=run_loop_mensagens_thread, args=(monitor, porta, num_conexoes, timeout, latencia,  qtd_exec, qtdterm, transacao, saved_text)).start()

loop_thread(monitor,porta,num_conexoes,timeout,latencia, qtd_exec, qtdterm, transacao, saved_text)
    