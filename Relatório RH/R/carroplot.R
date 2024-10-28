library(tidyverse)
library(fmsb)
library(scales)
library(showtext)
showtext_auto()
font_add_google("IBM Plex Sans", "plex-sans") # fonte do relatório para padronização. Obrigado ChatGPT por me falar dessa função.

## dimensionar valores por função, nível, setor
## quantidade de funcionários por setor, nível, etc

load("producao.RData")
load("reajuste.RData")
load("setorizado.RData")

# reajuste por categoria
ggplot(data = reajuste, aes(
  x = TOTAL,
  y = reorder(CATEGORIA, TOTAL)
)) +
  labs(title = "Investimento Mensal por Categoria",
       subtitle = "Total de recursos adicionais destinados a cada categoria",
       x = NULL,
       y = NULL) +
  geom_bar(stat = "identity", fill= "#6eaff1") +
  geom_vline(xintercept = 0, colour = "#ff7f0e") +
  scale_x_continuous(labels = 
                       label_dollar(prefix = "R$ ", scale = 1e-3,,
                                    big.mark = ".",
                                    suffix = "k")) +
  theme_minimal(base_family = "plex-sans") +
  theme(plot.title = element_text(size = 12, face = "bold"),
        plot.subtitle = element_text(size = 8, vjust = 3),
        axis.text.y = element_text(angle = 0, size = 6, face = "bold"),
        axis.text.x = element_text(size = 8)) 

# crescimento por função
## percent stacked barchart 

# usar o aumento salarial como argumento para o preenchimento

# - sumarizar os dados com base nos categorias, sem os níveis, para
# observar as categorias mais recomepensadas, depois fazer isso com os níveis

## gasto mensal

gasto <- producao |>
  summarise(Antigo = sum(SALÁRIO), Reajuste = sum(`NOVO SALÁRIO`)) |>
  pivot_longer(cols = everything(), 
               names_to = "Gasto", 
               values_to = "Valores")

# gasto$Diferença[1] <- 0
# asto$Diferença[2] <- gasto$Valores[2] - gasto$Valores[1]
# gasto <- rbind(gasto, tibble(Gasto = "Diferença", 
#                           Valores = gasto$Valores[2] - gasto$Valores[1]))

gasto <- cbind(gasto, Diferença = c(0, 14057))

ggplot(data = gasto, aes(x = Gasto, y = Valores, fill = Diferença)) +
  geom_bar(stat = "identity", position = "dodge", color = "black") +
  scale_y_continuous(
    labels = label_number(big.mark = ".", scale = 1e-3,
                          prefix = "R$ ", suffix = "k"),
    expand = expansion(mult = c(0, 0.1))
    ) +
  theme_minimal(base_family = "plex-sans") +
  labs(title = "Evolução dos Salários", 
       subtitle = "Impacto dos Reajustes Recentes") + 
  theme(
    plot.title = element_text(size = 12, face = "bold", hjust = 0.34),
    plot.subtitle = element_text(size = 10, face = "plain", , hjust = 0.34),
    axis.text.y = element_text(size = 6, face = "plain"), 
    axis.title.y = element_blank(),
    axis.title.x = element_blank(),
    legend.position = "none")

## gráficos de área e linha comparando crescimento do gasto anualmente
## mês a mês
 ## o crescimento é linear, pensar em outra coisa

# dumbbell plot - comparativo entre salários antes e depois

ggplot(data = reajuste, aes(x = PROPOSTA,
                            y = reorder(CATEGORIA, PROPOSTA))) +
  geom_segment(aes(x = PROPOSTA, xend = MED_OLD,
                   y = CATEGORIA, yend = CATEGORIA)) +
  geom_point(aes(x = PROPOSTA, y = CATEGORIA, 
                 size = 3, colour = "red"),
             show.legend = FALSE) +
  geom_point(aes(x = MED_OLD, y = CATEGORIA, 
                 size = 3, colour = "blue3"),
             show.legend = FALSE) +
  scale_x_continuous(expand = c(0.2, 0.3),
                     labels = label_number(
                       scale = 1e-3,
                       big.mark = ".", 
                       prefix = "R$ ", suffix = "k"),
  ) +
  theme_minimal(base_family = "plex-sans") +
  labs(title = "Comparação dos Salários Médios",
       subtitle = "Impacto do Reajuste nos Salários") +
  theme(plot.title = element_text(face = "bold", size = 12),
        plot.subtitle = element_text(face = "plain", vjust = 2, size = 10),
        axis.text.y = element_text(size = 8, face = "bold"),
        axis.text.x = element_text(size = 8, face = "bold"),
        axis.title.x = element_blank(),
        axis.title.y = element_blank(),
        plot.margin = margin(t = 10, r = 20, b = 7, l = 0))


ggplot(data = reajuste, aes(x = PROPOSTA, y = CATEGORIA)) +
  geom_segment(aes(x = PROPOSTA, xend = MED_OLD, 
                   y = CATEGORIA, yend = CATEGORIA)) +  
  geom_point(aes(x = PROPOSTA), 
             size = 3, colour = "#ff7f0e", show.legend = FALSE) +  
  geom_point(aes(x = MED_OLD), 
             size = 3, colour = "#1f77b4", show.legend = FALSE) +  
  scale_x_continuous(expand = c(0.2, 0.3),
                     labels = label_number(
                       scale = 1e-3,
                       big.mark = ".", 
                       prefix = "R$ ", suffix = "k")
  ) +
  theme_minimal(base_family = "plex-sans") +
  labs(title = "Comparação dos Salários Médios",
       subtitle = "Impacto do Reajuste nos Salários") +
  theme(plot.title = element_text(face = "bold", size = 12),
        plot.subtitle = element_text(face = "plain", vjust = 2, size = 10),
        axis.text.y = element_text(size = 8, face = "bold"),
        axis.text.x = element_text(size = 8, face = "bold"),
        axis.title.x = element_blank(),
        axis.title.y = element_blank(),
        plot.margin = margin(t = 10, r = 20, b = 7, l = 0))

## stacked bar plot

reajuste$NÍVEL[6] <- "3"

sbp <- reajuste |>
  ungroup() |>
  select(c("FUNÇÃO", "NÍVEL", "QTD", "PROPOSTA"))

sbp$TOTAL <- sbp$QTD * sbp$PROPOSTA
sbp$FUNÇÃO <- str_to_title(sbp$FUNÇÃO)
sbp <- sbp |> rename(Nível = NÍVEL)

ggplot(sbp, aes(fill = Nível, 
                     y = TOTAL,
                     x = reorder(FUNÇÃO, TOTAL))) +
  geom_bar(position="stack", stat="identity") +
  theme_minimal(base_family = "plex-sans") +
  labs(title = "Distribuição Salarial por Função",
       subtitle = "Gastos por Função na Folha de Pagamento") +
  scale_y_continuous(labels = label_number(
    scale = 1e-3,
    suffix = "k",
    big.mark = ".", decimal.mark = ",", 
    prefix = "R$ "),
  ) +
  scale_fill_manual(values = c("1" = "#ff7f0e", 
                               "2" = "#1f77b4", 
                               "3" = "#192b40")) +
  theme(plot.title = element_text(face = "bold", size = 12),
        plot.subtitle = element_text(face = "plain", size = 10),
        axis.title.x = element_blank(),
        axis.title.y = element_blank(),
        axis.text.x = element_text(size = 7))


# recursos por setor

## data wrangling
setorizado_longer <- setorizado |>
  pivot_longer(cols = c("Antigo_Salario", "Novo_Salario"),
               names_to = c("Gasto"), values_to = c("Valores"))

setorizado_longer <- setorizado_longer |>
  select(Setor, Gasto, Valores, Reajuste)

## plot

ggplot(setorizado_longer, aes(x = reorder(Setor, Valores), 
                       y = Valores, fill = Gasto)) +
  geom_bar(position = "dodge", stat = "identity") +
  scale_y_continuous(labels = label_number(
    scale = 1e-3,
    suffix = "k",
    big.mark = ".", decimal.mark = ",", 
    prefix = "R$ "),
  ) +
  scale_fill_manual(values = c("Antigo_Salario" = "#ff7f0e", 
                               "Novo_Salario" = "#1f77b4"),
                    labels = c("Antigo_Salario" = "Anterior",
                               "Novo_Salario" = "Novo")
  ) +
  labs(title = "Impacto dos Reajustes Salariais por Setor") +
  theme_minimal(base_family = "plex-sans") +
  theme(plot.title = element_text(face = "bold", size = 12),
        plot.subtitle = element_text(face = "plain", size = 10),
        axis.title.x = element_blank(),
        axis.title.y = element_blank(),
        axis.text.x = element_text(size = 6, angle = 20)) 
  

# setores mais beneficiados pela mudança

setorizado_wide <- setorizado |>
  select(Setor, Novo_Salario) |>
  pivot_longer(cols = Novo_Salario, names_to = "Tipo", values_to = "Valor") |>
  pivot_wider(names_from = Setor, values_from = Valor)

setorizadow <- setorizado_wide[,-1]

setorizadow <- rbind(rep(max(setorizado$Novo_Salario), 9), 
                     rep(min(setorizado$Novo_Salario), 9), 
                     setorizadow)

radarchart(setorizadow, pcol=rgb(0.08,0.14,0.21,0.8) , 
           pfcol=rgb(0.12,0.46,0.7,0.7) , plwd=4 , 
           cglcol="grey", cglty=1, axislabcol="grey", 
           caxislabels=seq(0,20,5), cglwd=0.8,
           vlcex=0.6, title = "Distribuição de Recursos"
) 

# perspectiva de carreira

p1 <- ggplot(sbp[-6,], aes(x = Nível, y = PROPOSTA, fill = Nível)) +
  geom_col() +
  geom_text(aes(label = label_number(
    scale = 1, suffix = ",00",
    big.mark = ",", decimal.mark = ".",
    prefix = "R$ ")(PROPOSTA)),
    position = position_stack(vjust = 0.5), 
    color = "white", size = 2) + 
  scale_fill_manual(values = c("3" = "#ff7f0e", 
                               "2" = "#1f77b4", 
                               "1" = "#192b40")) +
  theme_light(base_family = "plex-sans") + 
  theme(plot.title = element_text(face = "bold", size = 12),
        plot.subtitle = element_text(face = "plain", size = 10),
        axis.text.x = element_text(size = 10, face = "bold")) +
  scale_y_continuous(labels = label_number(
    scale = 1e-3,
    suffix = "k",
    big.mark = ",",
    prefix = "R$ "
  ))


p1 + 
  facet_wrap(~ FUNÇÃO, nrow = 4) + 
  labs(title = "Perspectivas de Progressão de Carreira",
       subtitle = "Possibilidades de aumento de salário no setor de produção",
       y = "Salários") +
  theme(axis.text.x = element_blank(),
        axis.title.x = element_blank(),
        axis.title.y = element_blank())  

