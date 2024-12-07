from supabase import create_client
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

# Configuração Supabase
supabase_url = "https://jumgqbwxvwdmyplzbkay.supabase.co"
supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp1bWdxYnd4dndkbXlwbHpia2F5Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczMzE0OTYxNiwiZXhwIjoyMDQ4NzI1NjE2fQ.kQCkHbZ19Jg7uLvNX9iEF-7Kkf_D2CcYHOL9h9tj-B8"

# Inicializa cliente Supabase
supabase = create_client(supabase_url, supabase_key)

def explore_database():
    # Lista todas as tabelas
    print("\n=== Explorando Banco de Dados ===")
    
    # Busca usuários
    print("\n=== Tabela users ===")
    users = supabase.table('users').select("*").execute()
    if users.data:
        print(f"\nNúmero de usuários: {len(users.data)}")
        print("\nEstrutura de um usuário:")
        for key in users.data[0].keys():
            print(f"- {key}")
        
        print("\nPrimeiro usuário como exemplo:")
        print(users.data[0])
    else:
        print("Nenhum usuário encontrado")
    
    # Busca outras tabelas relevantes
    print("\n=== Outras Tabelas ===")
    try:
        profiles = supabase.table('profiles').select("*").execute()
        print("\nTabela profiles encontrada")
        if profiles.data:
            print(f"Número de perfis: {len(profiles.data)}")
    except:
        print("Tabela profiles não encontrada")

if __name__ == "__main__":
    explore_database()
