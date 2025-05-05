# utils.py
def avancar_ano_serie(ano_atual):
    ordem = ["1º ANO", "2º ANO", "3º ANO", "4º ANO", "5º ANO"]
    try:
        pos = ordem.index(ano_atual.strip().upper())
        return ordem[pos + 1] if pos < len(ordem) - 1 else ano_atual
    except ValueError:
        return ano_atual
