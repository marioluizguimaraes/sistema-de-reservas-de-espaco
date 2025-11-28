require('dotenv').config();

const express = require('express'); // Framework web para criar a API
const axios = require('axios');     // Cliente HTTP para fazer requisições REST ao Django
const soap = require('soap');       // Cliente SOAP para comunicar com o serviço SOAP do Django
const cors = require('cors');       // Middleware para permitir requisições de outras origens (Cross-Origin)

// Inicializa a aplicação Express
const app = express();

// Configura o Express para entender JSON no corpo das requisições
app.use(express.json());

// Habilita CORS para que front-ends em outras portas/domínios possam acessar este Gateway
app.use(cors());

const PORT = process.env.PORT || 3000;
const DJANGO_URL = process.env.DJANGO_API_URL;
const SOAP_WSDL = process.env.DJANGO_SOAP_WSDL;

const addHateoas = (resourceType, item) => {

    if (!item || !item.id) return item;

    const links = [
        { rel: 'self', method: 'GET', href: `http://localhost:${PORT}/${resourceType}/${item.id}` },
        { rel: 'update', method: 'PUT', href: `http://localhost:${PORT}/${resourceType}/${item.id}` },
        { rel: 'partial_update', method: 'PATCH', href: `http://localhost:${PORT}/${resourceType}/${item.id}` },
        { rel: 'delete', method: 'DELETE', href: `http://localhost:${PORT}/${resourceType}/${item.id}` }
    ];

    if (resourceType === 'salas') {
        links.push({ 
            rel: 'reservar', 
            method: 'POST', 
            href: `http://localhost:${PORT}/reservas`,
            
            body_example: { sala: item.id, data_inicio: "YYYY-MM-DDTHH:MM", data_fim: "YYYY-MM-DDTHH:MM", forma_pagamento: "PIX" }
        });
        links.push({
            rel: 'relatorio_reservas',
            method: 'GET',
            href: `http://localhost:${PORT}/relatorios/sala/${item.id}`
        });
    }

    if (resourceType === 'reservas') {
        // Se a reserva está pendente, adicionamos opções de aprovação/cancelamento
        if (item.status === 'PENDENTE_APROVACAO') {
            links.push({ 
                rel: 'cancelar', 
                method: 'POST', 
                href: `http://localhost:${PORT}/reservas/${item.id}/cancelar` 
            });
            links.push({ 
                rel: 'aprovar_rejeitar', 
                method: 'POST', 
                href: `http://localhost:${PORT}/reservas/${item.id}/responder`,
                body_example: { acao: "APROVAR" } 
            });
        }
    }

    return { ...item, links: links };
};

app.post('/auth/:action', async (req, res) => {
    try {
        
        const response = await axios.post(`${DJANGO_URL}/auth/${req.params.action}/`, req.body);
        res.json(response.data);
        
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data || { error: 'Erro no Django' });
    }
});

// Listar todas as salas
app.get('/salas', async (req, res) => {
    try {
        
        const headers = req.headers.authorization ? { Authorization: req.headers.authorization } : {};
        const response = await axios.get(`${DJANGO_URL}/salas/`, { headers, params: req.query });
a
        if (response.data.results) {
            response.data.results = response.data.results.map(sala => addHateoas('salas', sala));
        }
        res.json(response.data);
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data);
    }
});

// Criar nova sala
app.post('/salas', async (req, res) => {
    try {
        const headers = { Authorization: req.headers.authorization };
        const response = await axios.post(`${DJANGO_URL}/salas/`, req.body, { headers });

        res.status(201).json(addHateoas('salas', response.data));
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data);
    }
});

// Detalhar uma sala específica
app.get('/salas/:id', async (req, res) => {
    try {
        const headers = req.headers.authorization ? { Authorization: req.headers.authorization } : {};
        const response = await axios.get(`${DJANGO_URL}/salas/${req.params.id}/`, { headers });
        
        res.json(addHateoas('salas', response.data));
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data);
    }
});

// Atualizar sala completa (PUT)
app.put('/salas/:id', async (req, res) => {
    try {
        const headers = { Authorization: req.headers.authorization };
        const response = await axios.put(`${DJANGO_URL}/salas/${req.params.id}/`, req.body, { headers });
        
        res.json(addHateoas('salas', response.data));
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data);
    }
});

// Atualizar sala parcialmente (PATCH)
app.patch('/salas/:id', async (req, res) => {
    try {
        const headers = { Authorization: req.headers.authorization };
        const response = await axios.patch(`${DJANGO_URL}/salas/${req.params.id}/`, req.body, { headers });
        
        res.json(addHateoas('salas', response.data));
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data);
    }
});

// Deletar sala
app.delete('/salas/:id', async (req, res) => {
    try {
        const headers = { Authorization: req.headers.authorization };
        await axios.delete(`${DJANGO_URL}/salas/${req.params.id}/`, { headers });

        res.status(204).send();
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data);
    }
});

// Listar reservas
app.get('/reservas', async (req, res) => {
    try {
        const headers = { Authorization: req.headers.authorization };
        const response = await axios.get(`${DJANGO_URL}/reservas/`, { headers, params: req.query });
        
        if (response.data.results) {
            response.data.results = response.data.results.map(reserva => addHateoas('reservas', reserva));
        }
        res.json(response.data);
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data);
    }
});

// Criar reserva
app.post('/reservas', async (req, res) => {
    try {
        const headers = { Authorization: req.headers.authorization };
        const response = await axios.post(`${DJANGO_URL}/reservas/`, req.body, { headers });
        res.status(201).json(addHateoas('reservas', response.data));
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data);
    }
});

// Detalhar reserva
app.get('/reservas/:id', async (req, res) => {
    try {
        const headers = { Authorization: req.headers.authorization };
        const response = await axios.get(`${DJANGO_URL}/reservas/${req.params.id}/`, { headers });
        res.json(addHateoas('reservas', response.data));
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data);
    }
});

// Atualizar reserva (PUT)
app.put('/reservas/:id', async (req, res) => {
    try {
        const headers = { Authorization: req.headers.authorization };
        const response = await axios.put(`${DJANGO_URL}/reservas/${req.params.id}/`, req.body, { headers });
        res.json(addHateoas('reservas', response.data));
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data);
    }
});

// Atualizar reserva (PATCH)
app.patch('/reservas/:id', async (req, res) => {
    try {
        const headers = { Authorization: req.headers.authorization };
        const response = await axios.patch(`${DJANGO_URL}/reservas/${req.params.id}/`, req.body, { headers });
        res.json(addHateoas('reservas', response.data));
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data);
    }
});

// Deletar reserva
app.delete('/reservas/:id', async (req, res) => {
    try {
        const headers = { Authorization: req.headers.authorization };
        await axios.delete(`${DJANGO_URL}/reservas/${req.params.id}/`, { headers });
        res.status(204).send();
    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data);
    }
});


// Mapeia ações customizadas (/cancelar, /responder)
app.post('/reservas/:id/:action', async (req, res) => {
    try {
        const headers = { Authorization: req.headers.authorization };
        const djangoActionUrl = `${DJANGO_URL}/reservas/${req.params.id}/${req.params.action}/`;
        
        const response = await axios.post(djangoActionUrl, req.body, { headers });
        res.json(response.data);

    } catch (error) {
        res.status(error.response?.status || 500).json(error.response?.data);
    }
});


app.get('/relatorios/sala/:id', (req, res) => {

    const args = {
        sala_id: req.params.id,
        limite: req.query.limite || 10,
        ordenacao: req.query.ordenacao || 'RECENTES'
    };

    // Cria o cliente SOAP usando o WSDL do Django
    soap.createClient(SOAP_WSDL, (err, client) => {
        if (err) {
            console.error("Erro SOAP:", err);
            return res.status(500).json({ error: 'Erro ao conectar no SOAP Django.' });
        }

        // Chama o método remoto 'gerar_relatorio_reservas'
        // O 3º argumento 'rawResponse' contém o XML bruto retornado pelo servidor
        client.gerar_relatorio_reservas(args, (err, result, rawResponse) => {
            if (err) return res.status(500).json({ error: 'Erro ao executar método SOAP', details: err.message });
            
            // Define o cabeçalho para 'text/xml'
            res.set('Content-Type', 'text/xml');
            res.send(rawResponse);
        });
    });
});

app.listen(PORT, () => {
    console.log(`Gateway rodando em: http://localhost:${PORT}`);
    console.log(`Conectado ao Django em: ${DJANGO_URL}`);
});