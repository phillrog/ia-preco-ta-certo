import re

def extrair_dados_etiqueta(res_texto):
    p = re.search(r'<p>(.*?)</p>', res_texto, re.I|re.S)
    v = re.search(r'<v>(.*?)</v>', res_texto, re.I|re.S)
    u = re.search(r'<u>(.*?)</u>', res_texto, re.I|re.S)
    return p, v, u

def processar_resposta(xml):
    # Extração do Total do Cupom
    total_cupom_lido = 0.0
    match_total = re.search(r'<total_nota>(.*?)</total_nota>', xml, re.S)
    if match_total:
        try:
            txt_total = match_total.group(1).upper().replace('R$', '').replace(' ', '')
            txt_total = txt_total.replace('.', '').replace(',', '.')
            total_cupom_lido = float(txt_total)
        except:
            total_cupom_lido = 0.0
            
    # Extração dos Itens
    items = re.findall(r'<item>(.*?)</item>', xml, re.S)
    res_c = []
    for it in items:
        n = re.search(r'<n>(.*?)</n>', it, re.S)
        s = re.search(r'<s>(.*?)</s>', it, re.S)
        d = re.search(r'<d>(.*?)</d>', it, re.S)
        
        status_texto = s.group(1).strip().upper() if s else "NÃO ENCONTRADO"
        res_c.append({
            "Produto": n.group(1).strip() if n else "", 
            "Status": status_texto, 
            "Observação": d.group(1).strip() if d else ""
        })
    return total_cupom_lido, res_c