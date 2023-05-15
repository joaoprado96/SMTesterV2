// Inicializa o Express.js, um framework de servidor web para Node.js.
const express = require('express');

//Para chamar a thread Python a partir do servidor Node.js
const { spawn } = require('child_process');

const app = express();

// Middleware para habilitar o CORS
app.use((req, res, next) => {
  res.header('Access-Control-Allow-Origin', 'http://localhost:3000'); // Altere para a origem correta do frontend
  res.header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept');
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
  next();
});

// Rota OPTIONS para lidar com a requisição preflight
app.options('/', (req, res) => {
  res.sendStatus(200);
});

// Configura o Express para utilizar o middleware que analisa as solicitações JSON.
app.use(express.json());

// Inicializa o contador de requisições
const requestCounter = {
  ACUMULADO: 0, 
  TOTAL: 0,
  GET: 0,
  POST: 0,
  PUT: 0,
  PATCH: 0,
  DELETE: 0,
  HEAD: 0,
  };

// Inicializa o banco de dados em memória com alguns dados de teste.
const database = [
  { clientId: '1', name: 'Nome de Cliente Normal' },
  { clientId: '$grbe', name: 'Testando o caracter dolar' },
];

// Middleware para adicionar um atraso às solicitações, com base no parâmetro de consulta "delay".
app.use((req, res, next) => {
  const delay = req.query.delay || 1;
  setTimeout(next, delay);
});

// Middleware para ajustar o status da resposta com base no parâmetro de consulta "status".
app.use((req, res, next) => {
  res.status(req.query.status || 200);
  next();
});

// Middleware para contar as requisições
app.use((req, res, next) => {
requestCounter.TOTAL++;
requestCounter[req.method]++;
next();
});

// Função para iniciar a thread
const startThread = (json) => {
  console.log('Thread iniciada');
  const pythonProcess = spawn('python3', ['script.py',JSON.stringify(json)]);

  pythonProcess.stdout.on('data', data => {
    // Tratar os dados de saída da thread Python, se necessário
    console.log(data.toString());
  });

  pythonProcess.stderr.on('data', data => {
    // Tratar os dados de erro da thread Python, se necessário
    console.error(data.toString());
  });

  pythonProcess.on('close', code => {
    // Executado quando a thread Python é encerrada
    console.log(`A thread Python foi encerrada com código de saída ${code}`);
  });
};

// Rota GET para buscar clientes por "clientId".
app.get('/',(req, res) => {
  const clientId = req.query.clientId;
  const client = database.find(client => client.clientId === clientId);
  if (client) {
    res.json({ message: 'Cliente encontrado', success: true, timestamp: new Date(), client });
  } else {
    res.json({ message: 'Cliente não encontrado', success: false, timestamp: new Date() });
  }
});

// Rotas POST, PUT, PATCH, DELETE, e HEAD, todas usando o middleware "nonGetHandler".
app.post('/', (req, res) => {
  // Armazena o JSON recebido na variável global
  jsonData = req.body;

  // Chamar a função startThread com a string desejada
  const stringParaThread = jsonData;
  startThread(stringParaThread);
  // Cria o objeto de resposta.
  const response = {
    message: 'POST request recebido',
    success: true,
    timestamp: new Date()
  };
  // Envia a resposta.
  res.json(response);
});

app.put('/', (req, res) => {
  res.json({  message: 'PUT request recebido', 
              success: true, 
              timestamp: new Date() });
});

app.patch('/', (req, res) => {
  res.json({  message: 'PATCH request recebido', 
              success: true, 
              timestamp: new Date() });
});

app.delete('/', (req, res) => {
  res.json({  message: 'DELETE request recebido', 
              success: true, 
              timestamp: new Date() });
});

app.head('/', (req, res) => {
  res.json({  message: 'HEAD request recebido', 
              success: true, 
              timestamp: new Date() });
});

// Midlewere para exibir a quantidade de requisições por segundo
setInterval(() => {
  console.log(`Requisições por segundo: ${JSON.stringify(requestCounter)}`);
  // Zerar o contador
  for (const method in requestCounter) {
    if (method !== 'ACUMULADO') {
      requestCounter[method] = 0;
    }
  }
}, 1000)

app.listen(8000, () => console.log('Backend do Service Master Tester'));
