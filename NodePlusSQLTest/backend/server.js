const express = require('express');
const mysql = require('mysql');
const bodyParser = require('body-parser');

const app = express();
const port = 3000;

app.use(bodyParser.json());

// MySQL connection
const db = mysql.createConnection({
    host: 'localhost',
    user: 'root', // Default user for XAMPP MySQL
    password: '', // Default password is empty
    database: 'node_mysql_db'
});

db.connect(err => {
    if (err) {
        throw err;
    }
    console.log('MySQL connected...');
});

// Create a new user
app.post('/user', (req, res) => {
    let newUser = { name: req.body.name, email: req.body.email };
    let sql = 'INSERT INTO users SET ?';
    let query = db.query(sql, newUser, (err, result) => {
        if (err) throw err;
        res.send('User added...');
    });
});

// Get all users
app.get('/users', (req, res) => {
    let sql = 'SELECT * FROM users';
    let query = db.query(sql, (err, results) => {
        if (err) throw err;
        res.json(results);
    });
});

// Get a single user by ID
app.get('/user/:id', (req, res) => {
    let sql = `SELECT * FROM users WHERE id = ${req.params.id}`;
    let query = db.query(sql, (err, result) => {
        if (err) throw err;
        res.json(result);
    });
});

// Update a user
app.put('/user/:id', (req, res) => {
    let updatedUser = { name: req.body.name, email: req.body.email };
    let sql = `UPDATE users SET ? WHERE id = ${req.params.id}`;
    let query = db.query(sql, updatedUser, (err, result) => {
        if (err) throw err;
        res.send('User updated...');
    });
});

// Delete a user
app.delete('/user/:id', (req, res) => {
    let sql = `DELETE FROM users WHERE id = ${req.params.id}`;
    let query = db.query(sql, (err, result) => {
        if (err) throw err;
        res.send('User deleted...');
    });
});

app.listen(port, () => {
    console.log(`Server started on port ${port}`);
});
