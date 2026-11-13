# StockControl — Sistema de Controle de Produção

> Sistema web full-stack para controle de estoque de matérias-primas e planejamento de produção industrial.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-5.x-092E20?style=flat&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.x-red?style=flat)
![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-7-646CFF?style=flat&logo=vite&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat&logo=sqlite&logoColor=white)

---

## 📋 Sobre o Projeto

O **StockControl** é um sistema de gestão de produção industrial desenvolvido como teste técnico full-stack. Permite controlar o estoque de insumos, cadastrar produtos e calcular automaticamente quais itens podem ser produzidos com base na disponibilidade de matérias-primas, priorizando os de maior valor para maximizar a receita.

---

## 🖥️ Screenshots

| Login |
|-------|
| <img width="1335" height="861" alt="image" src="https://github.com/user-attachments/assets/e10ba17a-b494-4658-8e9b-5c4165834fd9" />

| Dashboard |
|-----------|
| <img width="1911" height="854" alt="image" src="https://github.com/user-attachments/assets/0520e09c-cd0f-4697-91ee-df3da2f0d033" />

| Produtos |
|----------|
| <img width="1919" height="873" alt="image" src="https://github.com/user-attachments/assets/c1599114-3de7-4ce7-bc54-c4368c46f22e" />

| Produção |
|----------|
|<img width="1919" height="889" alt="image" src="https://github.com/user-attachments/assets/62271e55-7716-4e43-9520-19c3797253a2" />

---

## ⚙️ Funcionalidades

- ✅ Autenticação com JWT (login/logout)
- ✅ CRUD de Produtos com imagem
- ✅ CRUD de Matérias-Primas com controle de estoque
- ✅ Associação Produto × Matéria-Prima (Bill of Materials)
- ✅ Algoritmo de produção com priorização por maior valor
- ✅ Histórico de produção com métricas de receita
- ✅ Interface responsiva com tema escuro

---

## 🚀 Stack Tecnológica

### Back-end
| Tecnologia | Versão | Uso |
|---|---|---|
| Python | 3.11 | Linguagem principal |
| Django | 5.x | Framework web |
| Django REST Framework | 3.x | API RESTful |
| Simple JWT | — | Autenticação via token JWT |
| django-simple-history | 3.x | Auditoria de alterações |
| SQLite | — | Banco de dados |
| pytest + pytest-django | — | Testes automatizados |

### Front-end
| Tecnologia | Versão | Uso |
|---|---|---|
| React | 19 | Interface de usuário |
| Vite | 7 | Bundler / dev server |
| React Router DOM | 7 | Roteamento SPA |
| Axios | 1.x | Requisições HTTP |

---

## 🗂️ Estrutura de Pastas

```
stockcontrol/
├── .gitignore
├── README.md
│
├── Django/                          # Back-end
│   ├── core/                        # Configurações do projeto
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── production/                  # App principal
│   │   ├── migrations/
│   │   ├── models.py                # Product, RawMaterial, ProductionLog
│   │   ├── serializers.py
│   │   ├── views.py                 # ViewSets + can_produce / produce
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── tests/                   # Testes da API (pytest)
│   ├── manage.py
│   ├── pyproject.toml               # Configuração do pytest
│   ├── requirements.txt             # Dependências da aplicação
│   └── requirements-dev.txt         # + dependências de teste
│
└── React/                           # Front-end
    ├── public/
    └── src/
        ├── api/
        │   └── api.js               # Axios + interceptor JWT
        ├── components/
        │   ├── Navbar.jsx
        │   ├── Layout.jsx
        │   ├── ModalForm.jsx
        │   └── Spinner.jsx
        └── pages/
            ├── Login.jsx
            ├── Dashboard.jsx
            ├── Products.jsx
            ├── RawMaterials.jsx
            ├── ProductRawMaterials.jsx
            ├── Production.jsx
            └── EditForm.jsx
```

---

## 🔌 Endpoints da API

### Autenticação
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/api/token/` | Login — retorna access e refresh token |
| `POST` | `/api/token/refresh/` | Renova o access token |

### Produtos
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/products/` | Lista todos os produtos |
| `POST` | `/api/products/` | Cria um novo produto |
| `GET` | `/api/products/{id}/` | Detalhe de um produto |
| `PATCH` | `/api/products/{id}/` | Atualiza um produto |
| `DELETE` | `/api/products/{id}/` | Remove um produto |
| `GET` | `/api/products/{id}/can_produce/` | Verifica estoque para produzir |
| `POST` | `/api/products/{id}/produce/` | Registra a produção |

### Matérias-Primas
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/raw-materials/` | Lista todas as matérias-primas |
| `POST` | `/api/raw-materials/` | Cria uma matéria-prima |
| `PATCH` | `/api/raw-materials/{id}/` | Atualiza estoque / dados |
| `DELETE` | `/api/raw-materials/{id}/` | Remove uma matéria-prima |

### Associações e Produção
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/api/product-raw-materials/` | Lista todas as associações |
| `POST` | `/api/product-raw-materials/` | Cria associação produto × matéria-prima |
| `PATCH` | `/api/product-raw-materials/{id}/` | Edita quantidade da associação |
| `DELETE` | `/api/product-raw-materials/{id}/` | Remove associação |
| `GET` | `/api/production-logs/` | Histórico de produções |

---

## 🛠️ Como Rodar Localmente

### Pré-requisitos
- Python 3.11+
- Node.js 18+

### 1. Clone o repositório

```bash
git clone https://github.com/LLadeia/stockcontrol.git
cd stockcontrol
```

### 2. Back-end (Django)

```bash
cd Django

# Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows

# Instale as dependências
pip install -r requirements.txt

# Execute as migrações
python manage.py migrate

# Crie o usuário de teste
python manage.py shell -c "
from django.contrib.auth.models import User
User.objects.create_user('testuser', password='testpass123')
"

# Inicie o servidor
python manage.py runserver
```

API disponível em: `http://127.0.0.1:8000/api/`

### 3. Front-end (React)

```bash
cd React

# Instale as dependências
npm install

# Inicie o dev server
npm run dev
```

Interface disponível em: `http://localhost:5173`

### 4. Credenciais de Teste

```
Usuário: testuser
Senha:   testpass123
```

---

## 🧪 Testes

Os testes ficam em `Django/production/tests/` e usam **pytest** com **pytest-django**. Eles exercitam a API por HTTP (autenticação JWT, CRUDs e as ações `can_produce` e `produce`) em um banco de testes criado e descartado a cada execução.

```bash
cd Django
source venv/bin/activate                 # o mesmo ambiente virtual do back-end
pip install -r requirements-dev.txt

pytest                                   # roda a suíte
pytest --cov=production --cov=core       # com relatório de cobertura
```

Resultado esperado hoje: `99 passed, 13 xfailed`.

### Bugs conhecidos (falhas esperadas)

Os testes marcados com `xfail` descrevem o comportamento **correto** de pontos em que a aplicação ainda falha. Eles documentam os bugs sem quebrar a suíte; quando um bug for corrigido, o teste passa a funcionar e a marcação deve ser removida (`xfail_strict` faz a suíte acusar isso).

| Onde | Problema |
|---|---|
| `produce` | Quantidade inválida (`"abc"`, `null`, `"2.5"`...) gera erro 500 em vez de 400 |
| `produce` | Quantidade zero ou negativa é aceita (a negativa devolve matéria-prima ao estoque) |
| `produce` | Falha ao creditar o estoque do produto é ignorada e a produção é dada como concluída |
| `produce` | Estoque em ponto flutuante: `3 × 0,1 > 0,3` recusa uma produção que deveria caber |
| `produce` | Matéria-prima repetida na ficha técnica: só o débito da última linha é gravado |
| Migrações | Geradas com Django 6; no Django 5 do `requirements.txt` há uma migração pendente |

Para ver cada falha em detalhe: `pytest --runxfail`.

---

## 🧠 Algoritmo de Produção

O sistema calcula automaticamente a produção sugerida seguindo esta lógica:

1. Ordena os produtos por **maior valor unitário**
2. Para cada produto, calcula `floor(estoque / quantidade_necessária)` por matéria-prima
3. O **mínimo** entre todos os materiais define a quantidade máxima produzível
4. Os materiais são **debitados do estoque** em ordem de prioridade
5. Retorna o total de receita esperada com a produção otimizada

Isso garante que materiais compartilhados entre produtos sejam alocados primeiro para os itens de maior valor, maximizando a receita total.

---

## 👨‍💻 Autor

**Tadeu Ladeia**

[![GitHub](https://img.shields.io/badge/GitHub-LLadeia-181717?style=flat&logo=github)](https://github.com/LLadeia)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Tadeu_Ladeia-0A66C2?style=flat&logo=linkedin)](https://www.linkedin.com/in/tadeu-ladeia-4076b629b)

---

*Desenvolvido como teste técnico full-stack — Django REST Framework + React 19*
