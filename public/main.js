// Inicialização do Supabase
const supabaseUrl = 'sua-url-do-supabase';
const supabaseKey = 'sua-chave-do-supabase';
const supabase = supabase.createClient(supabaseUrl, supabaseKey);

// Inicialização do Stripe
const stripe = Stripe('sua-chave-publica-do-stripe');

// Estado da aplicação
let currentUser = null;

// Funções de autenticação
async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password
        });

        if (error) throw error;

        currentUser = data.user;
        showDashboard();
        await checkSubscription();
    } catch (error) {
        alert('Erro ao fazer login: ' + error.message);
    }
}

async function signup() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const { data, error } = await supabase.auth.signUp({
            email,
            password
        });

        if (error) throw error;

        alert('Cadastro realizado! Verifique seu email.');
    } catch (error) {
        alert('Erro ao cadastrar: ' + error.message);
    }
}

async function logout() {
    try {
        await supabase.auth.signOut();
        currentUser = null;
        showLoginForm();
    } catch (error) {
        alert('Erro ao sair: ' + error.message);
    }
}

// Funções de UI
function showDashboard() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
}

function showLoginForm() {
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('dashboard').style.display = 'none';
}

// Funções de assinatura
async function checkSubscription() {
    try {
        const response = await fetch('/api/check-subscription', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${supabase.auth.session()?.access_token}`
            }
        });
        
        const data = await response.json();
        
        const statusText = document.getElementById('statusText');
        const subscriptionButton = document.getElementById('subscriptionButton');
        
        if (data.subscribed) {
            statusText.textContent = 'Você tem uma assinatura ativa';
            subscriptionButton.textContent = 'Gerenciar Assinatura';
        } else {
            statusText.textContent = 'Você não tem uma assinatura ativa';
            subscriptionButton.textContent = 'Assinar Agora';
        }
    } catch (error) {
        console.error('Erro ao verificar assinatura:', error);
    }
}

async function handleSubscription() {
    try {
        const response = await fetch('/api/create-checkout-session', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${supabase.auth.session()?.access_token}`
            }
        });

        const session = await response.json();
        
        if (session.error) {
            throw new Error(session.error);
        }

        const result = await stripe.redirectToCheckout({
            sessionId: session.id
        });

        if (result.error) {
            throw new Error(result.error.message);
        }
    } catch (error) {
        alert('Erro ao iniciar checkout: ' + error.message);
    }
}

// Verificar estado inicial da autenticação
supabase.auth.onAuthStateChange((event, session) => {
    if (session) {
        currentUser = session.user;
        showDashboard();
        checkSubscription();
    } else {
        showLoginForm();
    }
});
