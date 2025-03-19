const express = require('express');
const multer = require('multer');
const mysql = require('mysql');
const xlsx = require('xlsx');
const cors = require('cors');
const jwt = require('jsonwebtoken');
const app = express();
const port = 5000;
const { spawn } = require('child_process');  // Usamos spawn en lugar de exec
// const moment = require('moment');  // Para manejar fechas fácilmente

// Middleware
app.use(cors());
app.use(express.json());

// Configura Multer para la subida de archivos
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Configura la conexión a MySQL LOCALHOST

// Configura la conexión a MySQL LOCALHOST
// const db = mysql.createConnection({
//   host: 'localhost',
//   user: 'root',     // Cambia por tu usuario de MySQL
//   password: '', // Cambia por tu contraseña de MySQL
//   database: 'beagle', // Cambia por el nombre de tu base de datos
// });

// const db = mysql.createConnection({
//   host: 'localhost',
//   user: 'jogatec_beagle',// Cambia por tu usuario de MySQL
//   password: 'Beagle2024', // Cambia por tu contraseña de MySQL
//   database: 'jogatec_beagle', // Cambia por el nombre de tu base de datos
// });


// Conectar a la base de datos
// db.connect((err) => {
//   if (err) {
//     console.error('Error de conexión: ' + err.stack);
//     return;
//   }
//   console.log('Conectado a la base de datos');
// });

// Middleware para parsear JSON
app.use(express.json());

// select u.id, u.usuario, u.clave, u.idrol, ifnull(r.rol, "s/n rol") as rol  from usuario u
// inner join rol r on r.id= u.idrol
// where u.usuario=? and u.clave=?
// Clave secreta para firmar el token
const SECRET_KEY = 'Beagle123';


//verifica token :
const verifyToken = (req, res, next) => {
  const bearerHeader = req.headers['authorization'];

  if (typeof bearerHeader !== 'undefined') {
    const token = bearerHeader.split(' ')[1];

    jwt.verify(token, SECRET_KEY, (err, decoded) => {
      if (err) {
        return res.sendStatus(403); // Forbidden
      }
      req.userId = decoded.id; // Guardar el ID del usuario en la solicitud
      next();
    });
  } else {
    res.sendStatus(403); // Forbidden
  }
};


//IDENTIFICA EL EMISOR DE LA FACTURA

app.post('/api/coordenadas', (req, res) => {
  const { base64, area_tabla, area_CABECERA } = req.body;

  if (!base64 || !area_tabla || !area_CABECERA) {
    return res.status(400).json({ error: 'Faltan datos en la solicitud.' });
  }

  const jsonData = JSON.stringify({ base64, area_tabla, area_CABECERA });

  console.log("Datos enviados a Python:", jsonData);

  // Asegurar que se use Python 3
  const pythonProcess = spawn('python', ['files_python/cut2.py']);

  let result = '';
  let errorOutput = '';

  pythonProcess.stdin.write(jsonData);
  pythonProcess.stdin.end();

  pythonProcess.stdout.on('data', (data) => {
    result += data.toString();
  });

  pythonProcess.stderr.on('data', (data) => {
    errorOutput += data.toString();
  });

  pythonProcess.on('close', (code) => {
    if (code !== 0 || errorOutput) {
      console.error(`Error en Python (código ${code}):`, errorOutput);
      return res.status(500).json({ error: 'Error en el script Python.', details: errorOutput });
    }

    try {
      const jsonResult = JSON.parse(result);
      res.json(jsonResult);
    } catch (error) {
      console.error(`Error al parsear JSON de Python: ${error.message}`);
      res.status(500).json({ error: 'Error al procesar la respuesta de Python.' });
    }
  });
});







app.listen(port, () => {
  console.log(`Servidor escuchando en http://localhost:${port}`);
});