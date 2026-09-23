import os,sys
os.environ["TCERO_MCP_SEM_AVISO_ATUALIZACAO"]="1"
sys.path.insert(0,"/Users/robertogrecia/MCP/tcero-jurisprudencia"); sys.path.insert(0,os.path.expanduser("~/.claude/skills/peticao-rg/scripts"))
import servidor_tcero as S, lint_citacoes as L
casos=[("em observância ao “princípio da legalidade estrita” aplicável","observância ao princípio da legalidade estrita aplicável"),
("o fornecimento de caixa d’água para a unidade escolar","fornecimento de caixa d água para a unidade escolar"),
("o fornecimento de caixa d’água para a unidade escolar","fornecimento de caixa dágua para a unidade escolar"),
("multa prevista no art. 55, II, da LC n° 154/96 aplicada","art. 55, II, da LC nº 154/96 aplicada"),
("decisão da 1ª Câmara deste Tribunal de Contas","decisão da 1a Câmara deste Tribunal"),
("julgou improcedentes os pedidos formulados pela defesa","procedentes os pedidos formulados pela defesa"),
("texto da ementa<br>segunda linha da ementa aqui","texto da ementa segunda linha da ementa"),
("aplicar multa&nbsp;ao responsável pelo descumprimento","aplicar multa ao responsável pelo descumprimento"),
("o conselheiro-substituto relatou o processo em sessão","conselheiro substituto relatou o processo"),
("com fundamento no art_5 inciso segundo da norma","fundamento no art 5 inciso segundo"),
]
for alvo,tr in casos:
    srv=S._verificar_trecho({"t":alvo},tr)["valido"]
    lin=(" "+L.norm_literal(tr)+" ") in (" "+L.norm_literal(alvo)+" "); sub=L.norm_literal(tr) in L.norm_literal(alvo)
    print(f"srv={srv!s:5} lint(sub)={sub!s:5} lint(word)={lin!s:5} | {tr}")
