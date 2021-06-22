# UPDATE - coronashooter
Aprimorar o jogo do repositório original.

## Estagio Inicial

Começamos o jogo a parti da fase 5, para isso criamos a branch copia_fase_5 no repositório [EzequielEBS/curso_pygame](https://github.com/EzequielEBS/curso_pygame/tree/copia_fase_5), onde trabalhos os updates.

## Quem fez?

## Dica

Para poder ver as fases novas, você pode tanto ver o vídeo disponível neste repositório como pode alterar os valores das variáveis nivel e pontuação.

# Alterações

* Mudamos o controle da nave.
* Adicionamos tela de start (com o fundo rolante) e game-over (com uma imagem fixa), assim o jogo nem começa e nem termina repentinamente.
* Adicionamos marcação de fase, pontos e vida.
* Agora, o botão "P" pause.
* Adicionamos músicas e efeitos sonoros (tiro, colisão, morte).
* Os sons podem ser controlados, com "M" ou "N", você pode pausar a música ou os efeitos sonoros e com "\[" e "\]" controlar o volume.
* As fases agora possuem transição, mudando os inimigos e o fundo.
* O movimento dos vírus mudam com a fase, tendo direção e velocidade aleatória na fase 1 e persegem o jogador no nível 2, para isso foram criadas novas classes que herdão da classe Virus.
* Alteramos também a difculdade do jogo, agora os vírus atiram e a nave pode se defender com o esculdo, apertando "E", bem como o tiro forte precisará ser conquistado com um novo item.

# Metas compridas!

Realizamos todos os critérios pedidos na entrega do trabalho. Como descrito abaixo.

## Elementos básicos

* Uso de sprites: não só permanecendo os sprites que já haviam, mas adicionamos os novos tiros e os novos vírus(os tiros são diferentes para cada vírus)
* Controle do movimento de sprites via código: Adicionamos isto no vírus da fase 1.
* Controle de um sprite via teclado: A nave é controlada por teclado (a qual mudamos o movimento).

## Novos elementos gráficos.

* Adicionamos novas telas e novos fundos
* Mudamos a imagem dos vírus

## Elementos sonoros

* O jogo tem duas músicas, uma para o jogo e outra para o menu, bem como os efeitos sonoros de explosão no game-over, barulho de tiro e barulho que indica colisão.

## Novas lógicas

* Temos o vírus inteligente na fase 2, que recebe a entrada da posição do inimigo para poder se mover em direção a ele. Além disso todos os vírus atiram.
* Mas não tema estas novas variantes! Agora há novas armas para vence-los, como o escudo e o item brilhante. Mas não adianta querer bater seu record batendo com o esculdo, os pontos não serão contadas!
* As fases têm transição, com a mudança de fundo.
* Além disso o pause com o botão "P" foi implementado.
