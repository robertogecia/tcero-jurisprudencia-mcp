exec(open("e2e.py").read())
import stat
print("perm", oct(os.stat(os.path.join(D,"98114.json")).st_mode & 0o777), oct(os.stat(D).st_mode & 0o777), "sha_campos" in rec)
lk=rec["link"]
def run(trecho):
    ficha={"chave":"APL-TC 00055/26","tribunal":"TCE-RO","id_documento":"98114","orgao":"Pleno",
           "relator":"José Euler Potyguara Pereira de Mello","data_julgamento":"22/06/2026","link":lk,
           "verificacao":"inteiro teor lido (PDF)","trecho":trecho}
    txt=f"Como decidiu o TCE-RO, “{trecho}” (APL-TC 00055/26, Pleno, Rel. José Euler Potyguara Pereira de Mello, j. 22/06/2026)."
    r=L.lint({"blocks":[{"tipo":"paragrafo","texto":txt}],"precedentes":[ficha],"dir_recibos_tcero":D})
    return r
t=rec["texto"]
ok="definir se o não atendimento, sem causa justificada, de determinações reiteradamente expedidas pelo Tribunal de Contas caracteriza descumprimento"
for nome,tr in [("1 real",ok),("2 troca",ok.replace("reiteradamente","repetidamente")),
                ("3 ia_dejur"," ".join(rec["texto_ia_dejur"].split()[5:20])),
                ("4 parecer", None)]:
    if tr is None:
        b=rec["texto_parecer_mpc"][2]; tr=" ".join(b.split()[:12]); print("   parecer excerpt:",tr)
    r=run(tr); print(nome, "ERROS:",[e[:110] for e in r.erros], "AVISOS:",[a[:110] for a in r.avisos])
# 5 voto (texto só no PDF), server verificar via recibo
v=" ".join(re.sub(r"\s+"," ",t[40000:40400]).split()[3:25]); print("5 voto", run(v).erros, S._verificar_trecho({"x":t},v)["valido"])
# servidor x lint em 200 trechos aleatórios do recibo, com aspas/ruído removidos
import random; random.seed(3); diverg=0
nt=re.sub(r"\s+"," ",t).split()
for _ in range(200):
    p=random.randrange(len(nt)-15); tr=" ".join(nt[p:p+12])
    a=S._verificar_trecho({"x":t},tr)["valido"]; b=L._contem_palavras(L.norm_literal(tr),L.norm_literal(t))
    if a!=b: diverg+=1; print("DIVERGE",a,b,tr)
print("divergências servidor×lint:",diverg,"/200")
