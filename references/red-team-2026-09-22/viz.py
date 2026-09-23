import os,sys,json,tempfile
sys.path.insert(0,os.path.expanduser("~/.claude/skills/peticao-rg/scripts")); import lint_citacoes as L
D=tempfile.mkdtemp()
def w(i,proc,texto): json.dump({"tribunal":"TCE-RO","id_documento":i,"nr_processo":proc,"texto":texto},open(f"{D}/{i}.json","w"))
w("98114","02603/22","o descumprimento injustificado de determinação caracteriza infração sujeita a multa")
# recibo de OUTRO processo cujo número (00055/26) coincide com o nº do ACÓRDÃO da ficha
w("11111","00055/26","a multa deve ser afastada quando o gestor comprova boa fé objetiva")
F=lambda **k: L.Ficha(dict({"chave":"APL-TC 00055/26","tribunal":"TCE-RO","id_documento":"98114","verificacao":"inteiro teor lido (PDF)"},**k),("x",))
print("colisao:",L.conferir_recibo(F(trecho="a multa deve ser afastada quando o gestor comprova boa fé"),None,None,None,D))
w("22222","02603/22","embargos de declaração rejeitados porque não há omissão a sanar no julgado")
print("irmao real:",L.conferir_recibo(F(trecho="embargos de declaração rejeitados porque não há omissão"),None,None,None,D))
for t in ("TCE/RO","TCERO","tce-ro","Tribunal de Contas do Estado de Rondônia","TCE-RO (Pleno)"):
    print(t, L.conferir_recibo(F(tribunal=t,trecho="texto inventado que não existe em lugar algum"),None,None,None,D)[:1])
print("int id", L._ids_da_ficha_tcero({"id_documento":98114}), L._ids_da_ficha_tcero({"id_documento":" 98114 "}), L._ids_da_ficha_tcero({"id_documento":98114.0}))
