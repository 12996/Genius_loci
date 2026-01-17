
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL='https://qellabwecrxngwuqofdh.supabase.co'
SUPABASE_KEY="sb_publishable_ormJ_ggEZRIpxaI3lp6qZQ_IACLFvzJ"

supabase: Client = create_client(
        SUPABASE_URL,
        SUPABASE_KEY,
)
