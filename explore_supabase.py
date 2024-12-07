from supabase import create_client

# Configurações do Supabase
SUPABASE_URL = "https://jumgqbwxvwdmyplzbkay.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp1bWdxYnd4dndkbXlwbHpia2F5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzE0OTYxNiwiZXhwIjoyMDQ4NzI1NjE2fQ.kQCkHbZ19Jg7uLvNX9iEF-7Kkf_D2CcYHOL9h9tj-B8"

# Criar cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Buscar todas as tabelas
print("Explorando estrutura do banco de dados...")

# Buscar dados da tabela de usuários
try:
    response = supabase.table('users').select("*").execute()
    print("\nEstrutura da tabela users:")
    if len(response.data) > 0:
        print("Colunas:", list(response.data[0].keys()))
        print("Exemplo de registro:", response.data[0])
except Exception as e:
    print("Erro ao acessar tabela users:", e)

# Buscar dados da tabela de assinaturas (se existir)
try:
    response = supabase.table('subscriptions').select("*").execute()
    print("\nEstrutura da tabela subscriptions:")
    if len(response.data) > 0:
        print("Colunas:", list(response.data[0].keys()))
        print("Exemplo de registro:", response.data[0])
except Exception as e:
    print("Erro ao acessar tabela subscriptions:", e)
