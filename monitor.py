import requests
from bs4 import BeautifulSoup
import os

# Puxa as informações sensíveis das variáveis de ambiente (Secrets do GitHub)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URL = "https://testcisia.it/calendario.php?tolc=cents&lingua=inglese"


def send_telegram(message):
    """Função simples para enviar mensagem via Bot do Telegram"""
    api_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(api_url, json=payload, timeout=10)
    except Exception as e:
        print(f"Erro ao enviar Telegram: {e}")


def check_cisia():
    print("Iniciando verificação no site do CISIA...")

    try:
        # 1. Faz o download da página
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(URL, headers=headers, timeout=15)
        response.raise_for_status()

        # 2. Parseia o HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Localiza a tabela pelo ID 'calendario'
        table = soup.find('table', id='calendario')
        if not table:
            print("Tabela não encontrada!")
            return

        rows = table.find('tbody').find_all('tr')
        vagas_encontradas = []

        # 3. Itera pelas linhas da tabela
        for row in rows:
            cols = row.find_all('td')

            # Verificação mínima de colunas para evitar erros de leitura
            if len(cols) >= 7:
                modalidade = cols[0].text.strip()  # Coluna 1: CENT@CASA ou CENT@UNI
                universidade = cols[1].text.strip()  # Coluna 2: Nome da Uni
                status = cols[6].text.strip().upper()  # Coluna 7: Status da vaga
                data_prova = cols[7].text.strip()  # Coluna 8: Data do teste

                # LOGICA: Apenas CENT@CASA e Status 'POSTI DISPONIBILI'
                if modalidade == "CENT@CASA" and "POSTI DISPONIBILI" in status:
                    info = f"🏛 <b>{universidade}</b>\n📅 Data: {data_prova}"
                    vagas_encontradas.append(info)

        # 4. Envia o alerta se houver vagas
        if vagas_encontradas:
            header_msg = "🚨 <b>VAGAS CENT@CASA DISPONÍVEIS!</b>\n\n"
            full_msg = header_msg + "\n\n".join(vagas_encontradas) + f"\n\n🔗 <a href='{URL}'>Reservar Agora</a>"
            send_telegram(full_msg)
            print(f"Sucesso! {len(vagas_encontradas)} vagas encontradas.")
        else:
            print("Nenhuma vaga CENT@CASA disponível.")

    except Exception as e:
        print(f"Ocorreu um erro durante a execução: {e}")


if __name__ == "__main__":
    # Garante que as variáveis existem antes de rodar
    if not TOKEN or not CHAT_ID:
        print("ERRO: TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não configurados nas variáveis de ambiente.")
    else:
        check_cisia()