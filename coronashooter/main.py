# -*- coding: UTF-8 -*-

import pygame
from pygame.locals import (DOUBLEBUF,
                           FULLSCREEN,
                           KEYDOWN,
                           KEYUP,
                           K_LEFT,
                           K_RIGHT,
                           QUIT,
                           K_ESCAPE, K_UP, K_DOWN, K_RCTRL, K_LCTRL,
                           K_r,
                           K_p,
                           K_m,
                           K_n,
                           K_LEFTBRACKET,
                           K_RIGHTBRACKET
                           )
from fundo import Fundo
from elementos import ElementoSprite
import random
import sys

class Jogo:
    def __init__(self, size=(700, 700), fullscreen=False):
        self.elementos = {}
        pygame.init()
        flags = DOUBLEBUF
        if fullscreen:
            flags |= FULLSCREEN

        self.tela = pygame.display.set_mode(size, flags=flags, depth=16)
        self.fundo = Fundo()
        self.jogador = None
        self.interval = 0
        self.nivel = 0
        pygame.font.init()
        self.fonte = pygame.font.SysFont("segoe-ui-symbol.ttf", 30)
        #SONS
        #música de fundo
        pygame.mixer.music.load('sons/musica_fundo.wav')
        pygame.mixer.music.play(-1)
        volume = pygame.mixer.music.get_volume()
        self.music = True
        #explosão
        self.explosao = pygame.mixer.Sound('sons/explosao.wav')
        pygame.mixer.Sound.set_volume(self.explosao, volume)
        #batida
        self.batida = pygame.mixer.Sound('sons/batida.wav')
        pygame.mixer.Sound.set_volume(self.batida, volume)
        #tiro
        self.som_tiro = pygame.mixer.Sound('sons/laser_shot.wav')
        pygame.mixer.Sound.set_volume(self.som_tiro, volume)
        #morte do vírus
        self.som_morte_virus = pygame.mixer.Sound('sons/morte_virus_som.wav')
        pygame.mixer.Sound.set_volume(self.som_morte_virus, volume)
        #música do menu
        self.musica_menu = pygame.mixer.Sound('sons/menu.wav')
        self.menu = True
        self.efeitos_sonoros = True
        self.screen_size = self.tela.get_size()
        pygame.mouse.set_visible(0)
        pygame.display.set_caption('Corona Shooter')
        self.run = True
        self.pause = False

    def manutenção(self):
        #Adiciona os vírus
        r = random.randint(0, 100)
        x = random.randint(1, self.screen_size[0])
        virii = self.elementos["virii"]
        if self.nivel == 0:
            qtd = 50
        elif self.nivel == 1:
            qtd = 30
        elif self.nivel == 2:
            qtd = 20
        if r > (qtd * len(virii)):
            if self.nivel == 0:
                enemy = Virus([0, 0])
            elif self.nivel == 1:
                enemy = Virus_aleatorio([0, 0])
            elif self.nivel == 2:
                enemy = Virus_inteligente([0, 0])
            size = enemy.get_size()
            enemy.set_pos([min(max(x, size[0] / 2), self.screen_size[0] - size[0] / 2), size[1] / 2])
            colisores = pygame.sprite.spritecollide(enemy, virii, False)
            if colisores:
                return
            self.elementos["virii"].add(enemy)
            
        #Adiciona os sprites de poder
        if (self.jogador.pontos%100 == 0) & (self.jogador.pontos!=0):
            r = random.randint(0, 100)
            x = random.randint(1, self.screen_size[0])
            poder = self.elementos["poder"]
            if r > (100 * len(poder)):
                item = Poder([0, 0])
                size = item.get_size()
                item.set_pos([min(max(x, size[0] / 2), self.screen_size[0] - size[0] / 2), size[1] / 2])
                colisores = pygame.sprite.spritecollide(item, poder, False)
                if colisores:
                    return
                self.elementos["poder"].add(item)
            

    def liga_desliga_musica(self):
        if self.music:
            pygame.mixer.music.pause()
            self.music = False
        else:
            pygame.mixer.music.unpause()
            self.music = True
        if self.menu:
            pygame.mixer.Sound.set_volume(self.musica_menu,0)
            self.menu = False
        else:
            volume_musica = pygame.mixer.music.get_volume()
            pygame.mixer.Sound.set_volume(self.musica_menu,volume_musica)
            self.menu = True
            
    def liga_desliga_efeitos_sonoros(self):
        lista_sons = [self.explosao, self.batida, self.som_tiro, self.som_morte_virus]
        if self.efeitos_sonoros:
            for sons in lista_sons:
                pygame.mixer.Sound.set_volume(sons,0)
            self.efeitos_sonoros = False
        else:
            for sons in lista_sons:
                volume_musica = pygame.mixer.music.get_volume()
                pygame.mixer.Sound.set_volume(sons,volume_musica)
            self.efeitos_sonoros = True
            
    def ajusta_volume(self,m):
        volume = pygame.mixer.music.get_volume()
        lista_sons = [self.explosao, self.batida, self.som_tiro, self.som_morte_virus, self.musica_menu]
        volume *= m
        if volume > 1:
            volume = 1
        if volume < 0.1:
            volume = 0.1
        pygame.mixer.music.set_volume(volume)
        
        for som in lista_sons:
            volume = pygame.mixer.Sound.get_volume(som)
            volume *= m
            if volume > 1:
                volume = 1
            if volume < 0.1:
                volume = 0.1
            pygame.mixer.Sound.set_volume(som, volume)
        
            
    def muda_nivel(self):
        xp = self.jogador.get_pontos()
        if xp > 100 and self.nivel == 0:
            self.fundo = Fundo("espaco1.png")
            self.nivel = 1
            self.jogador.set_lives(self.jogador.get_lives() + 3)
        elif xp > 300 and self.nivel == 1:
            self.fundo = Fundo("espaco2.jpg")
            self.nivel = 2
            self.jogador.set_lives(self.jogador.get_lives() + 6)

    def atualiza_elementos(self, dt):
        self.fundo.update(dt)
        for v in self.elementos.values():
            try:
                v.update(dt, position_jogador = self.jogador.get_pos()[0]) # rodar se o vírus for inteligente
            except TypeError:
                v.update(dt)

    def desenha_elementos(self):
        self.fundo.draw(self.tela)
        for v in self.elementos.values():
            v.draw(self.tela)

    def verifica_impactos(self, elemento, list, action):
        if isinstance(elemento, pygame.sprite.RenderPlain):
            hitted = pygame.sprite.groupcollide(elemento, list, 1, 0)
            for v in hitted.values():
                for o in v:
                    action(o)
                    pygame.mixer.Sound.play(self.som_morte_virus)
            return hitted

        elif isinstance(elemento, pygame.sprite.Sprite):
            if pygame.sprite.spritecollide(elemento, list, 1):
                action()
                pygame.mixer.Sound.play(self.batida)
            return elemento.morto


    def ação_elemento(self):
        self.verifica_impactos(self.jogador, self.elementos["tiros_inimigo"],
                               self.jogador.alvejado)
        if self.jogador.morto:
            pygame.mixer.Sound.play(self.explosao)
            self.run = False
            return

        # Verifica se o personagem trombou em algum inimigo
        self.verifica_impactos(self.jogador, self.elementos["virii"],
                               self.jogador.colisão)
        
        if self.jogador.morto:
            pygame.mixer.Sound.play(self.explosao)
            self.run = False
            return
        # Verifica se o personagem atingiu algum alvo.
        hitted = self.verifica_impactos(self.elementos["tiros"],
                                        self.elementos["virii"],
                                        Virus.alvejado)
            
        # Aumenta a pontos baseado no número de acertos:
        self.jogador.set_pontos(self.jogador.get_pontos() + len(hitted))
        
        # Verifica se o personagem adquiriu uma arma especial.
        self.verifica_impactos(self.jogador,
                               self.elementos["poder"],
                               self.jogador.modo_super)

    def trata_eventos(self):
        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            self.run = False

        if event.type in (KEYDOWN, KEYUP):
            key = event.key
            if key == K_ESCAPE:
                self.run = False
            elif key in (K_LCTRL, K_RCTRL):
                self.interval = 0
                self.jogador.atira(self.elementos["tiros"])
                pygame.mixer.Sound.play(self.som_tiro)

        if event.type == KEYDOWN:
            key = event.key
            if key == K_UP:
                self.jogador.accel_top()
            if key == K_DOWN:
                self.jogador.accel_bottom()
            elif key == K_RIGHT:
                self.jogador.accel_right()
            elif key == K_LEFT:
                self.jogador.accel_left()
            elif key == K_p:
                self.pause = not self.pause
            elif key == K_m:
                self.liga_desliga_musica()
                # self.music = not self.music
            elif key == K_n:
                self.liga_desliga_efeitos_sonoros()
            elif key == K_LEFTBRACKET:
                self.ajusta_volume(0.9)
            elif key == K_RIGHTBRACKET:
                self.ajusta_volume(1.1)

        if event.type == KEYUP:
            key = event.key
            if key == K_UP:
                self.jogador.set_speed((self.jogador.get_speed()[0], 0))
            if key == K_DOWN:
                self.jogador.set_speed((self.jogador.get_speed()[0], 0))
            elif key == K_RIGHT:
                self.jogador.set_speed((0, self.jogador.get_speed()[1]))
            elif key == K_LEFT:
                self.jogador.set_speed((0, self.jogador.get_speed()[1]))

        keys = pygame.key.get_pressed()
        if self.interval > 10:
            self.interval = 0
            if keys[K_RCTRL] or keys[K_LCTRL]:
                self.jogador.atira(self.elementos["tiros"])

    def escreve_textos(self):
        vidas = self.fonte.render(f'Vidas: {self.jogador.get_lives():3}', True,(255,255,255))
        pontuacao = self.fonte.render(f'Pontos: {self.jogador.get_pontos()}',True,(255,255,255))
        nivel = self.fonte.render(f'Nível: {self.nivel}', True, (255,255,255))
        simbolo_pause = self.fonte.render("||", True, (255,255,255))
        self.tela.blit(vidas,(0,0))
        self.tela.blit(pontuacao,(550,0))
        self.tela.blit(nivel,(300,0))
        if self.pause == True:
            self.tela.blit(simbolo_pause, (5,20))

    def tela_inicial(self, dt):
        fonte_grande =  pygame.font.SysFont("comicsansms", 70)
        fonte_pequena =  pygame.font.SysFont("comicsansms", 30)
        
        mensagem_inicio = fonte_grande.render('Coronashooter',True, (255, 255, 255))
        mensagem_começar = fonte_pequena.render('Pressione qualquer tecla para iniciar',True, (255, 255, 255))
        
        #centrlizar
        rect_inicio = mensagem_inicio.get_rect()
        rect_começar = mensagem_começar.get_rect()
        rect_inicio.centerx = rect_começar.centerx = self.tela.get_size()[0]//2
        rect_inicio.centery = 300
        rect_começar.centery = 400
        
        #imagem_fundo = pygame.image.load('./imagens/inicio.jpg').convert()
        #imagem_fundo =  pygame.transform.scale(imagem_fundo, (700,700))
        
        clock = pygame.time.Clock()
        inicio = True
        while inicio:
            clock.tick(1000 / dt)
            self.atualiza_elementos(dt)
            self.desenha_elementos()
            self.tela.blit(mensagem_inicio,rect_inicio)
            self.tela.blit(mensagem_começar,rect_começar)
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    inicio = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    inicio = False
                    pygame.mixer.Sound.stop(self.musica_menu)
                    
            pygame.display.flip()
            
            
    def muda_pause(self):
        pygame.mixer.music.pause()
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_p:
                self.pause = False
                pygame.mixer.music.unpause()

    def game_over(self):
        over = True
        imagem_fundo = pygame.image.load('./imagens/game-over.jpeg').convert()
        imagem_fundo =  pygame.transform.scale(imagem_fundo, self.tela.get_size())
        if self.music:
            volume_background = pygame.mixer.music.get_volume()
            pygame.mixer.Sound.set_volume(self.musica_menu,volume_background)
        pygame.mixer.Sound.play(self.musica_menu)
        
        while over:
            pygame.mixer.music.pause()
            self.tela.blit(imagem_fundo, (0,0))
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    over = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                        over = False
                    if event.key == K_r:
                        over = False
                        pygame.mixer.Sound.stop(self.musica_menu)
            pygame.display.flip()
    
    def loop(self):
        dt = 16
        pygame.mixer.music.pause()
        pygame.mixer.Sound.play(self.musica_menu)
        self.tela_inicial(dt)
        
        while True:
            pygame.mixer.Sound.stop(self.musica_menu)
            pygame.mixer.music.unpause()
            clock = pygame.time.Clock()
            self.elementos['virii'] = pygame.sprite.RenderPlain(Virus([120, 50]))
            self.jogador = Jogador([200, 400], 5)
            self.elementos['jogador'] = pygame.sprite.RenderPlain(self.jogador)
            self.elementos['tiros'] = pygame.sprite.RenderPlain()
            self.elementos['tiros_inimigo'] = pygame.sprite.RenderPlain()
            self.elementos['poder'] = pygame.sprite.RenderPlain(Poder([1500,1000]))
            while self.run:
                clock.tick(1000 / dt)
                if not self.pause:
                    
                    self.trata_eventos()
                    self.ação_elemento()
                    self.manutenção()
                    self.muda_nivel()
                    
                    # Atualiza Elementos
                    self.atualiza_elementos(dt)
                    
                    # Desenhe no back buffer
                    self.desenha_elementos()
                    self.escreve_textos()
                    
                    # Atualiza o tempo de  arma especial
                    if self.jogador.timer > 0:
                        self.jogador.timer = self.jogador.timer - 0.1
                    if self.jogador.timer <= 0:
                        self.jogador.poder_adquirido = 0

                        
                    pygame.display.flip()
                else:
                    self.muda_pause()
                  
            if self.jogador.morto:
                if self.music:
                    volume_background = pygame.mixer.music.get_volume()
                    pygame.mixer.Sound.set_volume(self.musica_menu,volume_background)
                self.game_over()
                J.__init__() # Reinicia valores para o novo jogo
            else:
                pygame.quit()
                sys.exit()
                break


class Nave(ElementoSprite):
    def __init__(self, position, lives=0, speed=[0, 0], image=None, new_size=[83, 248], poder_adquirido = None):
        self.timer = 0
        self.acceleration = [6, 6]
        if not poder_adquirido:
            self.poder_adquirido = 0
        if not image:
            self.image = "seringa.png"
        super().__init__(image, position, speed, new_size)
        self.set_lives(lives)

    def get_lives(self):
        return self.lives

    def set_lives(self, lives):
        self.lives = lives

    def colisão(self):
        if self.get_lives() <= 0:
            self.kill()
        else:
            self.set_lives(self.get_lives() - 1)

    def atira(self, lista_de_tiros, image=None):
        s = list(self.get_speed())
        s[1] *= 2
        Tiro(self.get_pos(), s, image, lista_de_tiros)
        

    def alvejado(self):
        if self.get_lives() <= 0:
            self.kill()
        else:
            self.set_lives(self.get_lives() - 1)
    
    def modo_super(self):
        self.poder_adquirido += 1
        self.timer += 30

    @property
    def morto(self):
        return self.get_lives() == 0

    def accel_top(self):
        speed = self.get_speed()
        self.set_speed((speed[0], speed[1] - self.acceleration[1]))

    def accel_bottom(self):
        speed = self.get_speed()
        self.set_speed((speed[0], speed[1] + self.acceleration[1]))

    def accel_left(self):
        speed = self.get_speed()
        self.set_speed((speed[0] - self.acceleration[0], speed[1]))

    def accel_right(self):
        speed = self.get_speed()
        self.set_speed((speed[0] + self.acceleration[0], speed[1]))


class Virus(Nave):
    def __init__(self, position, lives=1, speed=None, image=None, size=(100, 100)):
        if not image:
            image = "virus.png"
        super().__init__(position, lives, speed, image, size)


class Virus_inteligente(Virus):
    def __init__(self, position, lives=1, speed=None, image=None, size=(100, 100)):
        if not image:
            image = "virus2.png"
        super().__init__(position, lives=1, speed=None, image=image, size=(100, 100))
        self.acceleration = [1, 1]
        
    def update(self, dt, position_jogador=350):
        #inteligência, seguir o jogador
        if position_jogador < self.get_pos()[0]-10:
            self.set_speed((-4, self.get_speed()[1]))
        elif position_jogador > self.get_pos()[0]+10:
            self.set_speed((4, self.get_speed()[1]))
        else:
            self.set_speed((0, self.get_speed()[1]))
           
        move_speed = (self.speed[0] * dt / 16,
                      self.speed[1] * dt / 16)
        self.rect = self.rect.move(move_speed)
        if (self.rect.left > self.area.right) or \
                (self.rect.top > self.area.bottom) or \
                (self.rect.right < 0):
            self.kill()
        if (self.rect.bottom < - 40):
            self.kill()

class Virus_aleatorio(Virus):
    def __init__(self, position, lives=1, speed=None, image=None, size=(100, 100)):
        if not image:
            image = "virus1.png"
        super().__init__(position, lives, speed, image, size)
        self.acceleration = [1, 1]
        v = random.randint(-10,10)
        self.set_speed((v, self.get_speed()[1]))

    def update(self, dt):
        if self.get_pos()[0] < 100:
            v = random.randint(0,10)
            self.set_speed((v, self.get_speed()[1]))
        elif self.get_pos()[0] > 600:
            v = random.randint(-10,0)
            self.set_speed((v, self.get_speed()[1]))

        move_speed = (self.speed[0] * dt / 16,
                      self.speed[1] * dt / 16)
        self.rect = self.rect.move(move_speed)
        if (self.rect.left > self.area.right) or \
                (self.rect.top > self.area.bottom) or \
                (self.rect.right < 0):
            self.kill()
        if (self.rect.bottom < - 40):
            self.kill()

class Jogador(Nave):
    """
    A classe Player é uma classe derivada da classe GameObject.
       No entanto, o personagem não morre quando passa da borda, este só
    interrompe o seu movimento (vide update()).
       E possui experiência, que o fará mudar de nivel e melhorar seu tiro.
       A função get_pos() só foi redefinida para que os tiros não saissem da
    parte da frente da nave do personagem, por esta estar virada ao contrário
    das outras.
    """

    def __init__(self, position, lives=10, image=None, new_size=[83, 248]):
        if not image:
            image = "seringa.png"
        super().__init__(position, lives, [0, 0], image, new_size)
        self.pontos = 0

    def update(self, dt):
        move_speed = (self.speed[0] * dt / 16,
                      self.speed[1] * dt / 16)
        self.rect = self.rect.move(move_speed)

        if (self.rect.right > self.area.right):
            self.rect.right = self.area.right

        elif (self.rect.left < 0):
            self.rect.left = 0

        if (self.rect.bottom > self.area.bottom):
            self.rect.bottom = self.area.bottom

        elif (self.rect.top < 0):
            self.rect.top = 0

    def get_pos(self):
        return (self.rect.center[0], self.rect.top)

    def get_pontos(self):
        return self.pontos

    def set_pontos(self, pontos):
        self.pontos = pontos

    def atira(self, lista_de_tiros, image=None):
        l = 1
        if self.poder_adquirido >= 1: l = 3
        if self.poder_adquirido >= 2: l = 5

        p = self.get_pos()
        speeds = self.get_fire_speed(l)
        for s in speeds:
            Tiro(p, s, image, lista_de_tiros)
        

    def get_fire_speed(self, shots):
        speeds = []

        if shots <= 0:
            return speeds

        if shots == 1:
            speeds += [(0, -5)]

        if shots > 1 and shots <= 3:
            speeds += [(0, -5)]
            speeds += [(-2, -3)]
            speeds += [(2, -3)]

        if shots > 3 and shots <= 5:
            speeds += [(0, -5)]
            speeds += [(-2, -3)]
            speeds += [(2, -3)]
            speeds += [(-4, -2)]
            speeds += [(4, -2)]

        return speeds


class Tiro(ElementoSprite):
    def __init__(self, position, speed=None, image=None, list=None):
        if not image:
            image = "tiro.png"
        super().__init__(image, position, speed)
        if list is not None:
            self.add(list)


class Poder(ElementoSprite):
    def __init__(self, position, image=None, speed=None, new_size=(100,100)):
        if not image:
            image = "poder.png"
        super().__init__(image, position, speed, new_size)


if __name__ == '__main__':
        J = Jogo()
        J.loop()
