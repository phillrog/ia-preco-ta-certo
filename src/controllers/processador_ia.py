import re

def extrair_dados_etiqueta(res_texto):
    p = re.search(r'<p>(.*?)</p>', res_texto, re.I|re.S)
    v = re.search(r'<v>(.*?)</v>', res_texto, re.I|re.S)
    u = re.search(r'<u>(.*?)</u>', res_texto, re.I|re.S)
    ve = re.search(r'<ve>(.*?)</ve>', res_texto, re.I|re.S)
    v_extenso = ve.group(1).strip() if ve else ""
    
    return p, v, u, v_extenso

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
        
    match_extenso = re.search(r'<te>(.*?)</te>', xml, re.I|re.S)
    total_extenso = match_extenso.group(1).strip() if match_extenso else ""
    return total_cupom_lido, res_c, total_extenso

def valor_por_extenso(valor_float):
    """Converte um valor float para uma string amigável para narração."""
    try:
        # Separa reais de centavos
        reais = int(valor_float)
        centavos = int(round((valor_float - reais) * 100))
        
        texto_reais = f"{reais} {'real' if reais == 1 else 'reais'}"
        texto_centavos = f" e {centavos} centavos" if centavos > 0 else ""
        
        return f"{texto_reais}{texto_centavos}"
    except:
        return "valor não identificado"