library(tidyverse)
library(openxlsx)
# library(xtable)

funcionarios <- readxl::read_excel("CATEGORIAS.xlsx", sheet = 2)
salariosp <- readxl::read_excel("CATEGORIAS.xlsx", sheet = 3)

# configurando cabeçalho
salariosp[1,] -> cabec
salariosp[-1,] -> salariosp
colnames(salariosp) <- cabec
rm(cabec)
salariosp <- salariosp[,1:2]

# selecionando apenas colunas preenchidas e ajeitando cabeçalho
funcionarios[,c(1, 2, 5, 6, 7, 8, 10)] -> funcionarios
cabec <- funcionarios[1,]
funcionarios <- funcionarios[-1,]
colnames(funcionarios) <- cabec
colnames(funcionarios)[6] <- "Categoria"
rm(cabec)

# ajeitando formatação e realizando união das duas tabelas
salariosp$Categoria <- str_to_upper(salariosp$Categoria)

funcionarios <- funcionarios |>
  left_join(salariosp, by = "Categoria")

colnames(funcionarios)[6] <- "CATEGORIA"
colnames(funcionarios)[8] <- "NOVO SALÁRIO"
funcionarios$SALÁRIO <- as.numeric(funcionarios$SALÁRIO)
funcionarios$`NOVO SALÁRIO` <- as.numeric(funcionarios$`NOVO SALÁRIO`)

# definindo setor e removendo linhas e colunas inúteis
funcionarios$DEPARTAMENTO <- NA
funcionarios$DEPARTAMENTO[2:15] <- c("Administrativo")
funcionarios$DEPARTAMENTO[18:94] <- "Produção"
funcionarios <- funcionarios[-c(1, 16),]
funcionarios <- funcionarios[,-c(1,2)]

# setor produção
producao <- funcionarios[funcionarios$DEPARTAMENTO == "Produção",]

rm(funcionarios)

# filtrar os que terão um novo salário
producao <- filter(producao, !is.na(producao$`NOVO SALÁRIO`))

# reajuste
producao$REAJUSTE <- producao$`NOVO SALÁRIO` - producao$SALÁRIO

# custo total
total = sum(producao$`NOVO SALÁRIO`) - sum(producao$SALÁRIO)

# selecionando e ordernando colunas
producao <- producao |>
   select(NOME, SETOR, CATEGORIA, SALÁRIO, `NOVO SALÁRIO`, REAJUSTE) |>
   separate(CATEGORIA, into = c("FUNÇÃO", "NÍVEL"), sep = " ", remove = FALSE)
producao[producao$FUNÇÃO == "ENCARREGADO",]$NÍVEL <- "ENC"

# reajuste total por categoria

reajuste <- producao |>
  group_by(CATEGORIA) |>
  left_join(salariosp, by = c("CATEGORIA" = "Categoria")) |>
  summarise(QTD = n(),
            TOTAL = sum(REAJUSTE), 
            PROPOSTA = as.numeric(Salário), 
            MED_OLD = mean(SALÁRIO),
            ) |>
  distinct() |>
  separate(CATEGORIA, into = c("FUNÇÃO", "NÍVEL"), sep = " ", remove = FALSE)
reajuste[reajuste$FUNÇÃO == "ENCARREGADO",]$NÍVEL <- "ENC"

rm(salariosp)

# formatando para output

producao$SETOR <- producao$SETOR |> 
  str_extract("^[^ ]+") |>
  str_replace_all("REFORMAS", "REFORMA")

setorizado <- producao |> 
  group_by(SETOR) |>
  summarise(QTD = n(),
            Antigo_Salario = sum(SALÁRIO),
            Reajuste = sum(REAJUSTE),
            Novo_Salario = sum(`NOVO SALÁRIO`))

setorizado <- setorizado |> 
  rename(Setor = SETOR)

setorizado$Setor <- str_to_title(setorizado$Setor)


# salvando

save(producao, file = "producao.RData")
save(reajuste, file = "reajuste.RData")
save(setorizado, file = "setorizado.RData")

# anonimizando os dados
## producao$NOME <- paste("Funcionário", 1:52)

# salvando no formato excel
## openxlsx::write.xlsx(producao, file = "reajuste.xlsx")

# formatando para LaTeX

# reajuste <- reajuste |>
#   mutate(TOTAL = paste0("R$ ", format(TOTAL, nsmall = 2)),
#          PROPOSTA = paste0("R$ ", format(PROPOSTA, nsmall = 2)),
#          MED_OLD = paste0("R$ ", format(MED_OLD, nsmall = 2)),
#          )

# producao

# producao$NOME <- str_extract(producao$NOME, "^[^ ]+ [^ ]+")
## producao$NOME <- str_to_title(producao$NOME)
# producao <- producao |>
#   mutate(SALÁRIO = paste0("R$ ", format(SALÁRIO, nsmall = 2)),
#          `NOVO SALÁRIO` = paste0("R$ ", format(`NOVO SALÁRIO`, nsmall = 2)),
#          REAJUSTE = paste0("R$ ", format(REAJUSTE, nsmall = 2))
#            )
## print(xtable(producao[,-c(2, 3, 4, 5)], row.names = FALSE), 
##        include.rownames = FALSE, type = "latex")
## print(xtable(setorizado, row.names = FALSE), 
##      include.rownames = FALSE, type = "latex")
