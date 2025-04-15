from supabase import create_client
import uuid

SUPABASE_URL = 'https://SEU-PROJETO.supabase.co'  # coloque seu URL real
SUPABASE_KEY = 'chave-API-anon'                  # coloque sua chave real

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_imagem_arquivo(file, pasta="fotos_alunos"):
    filename = f"{uuid.uuid4()}.jpg"

    supabase.storage.from_("imagens").upload(
        f"{pasta}/{filename}",
        file,
        {"content-type": file.content_type}
    )

    url = f"{SUPABASE_URL}/storage/v1/object/public/imagens/{pasta}/{filename}"
    return url
