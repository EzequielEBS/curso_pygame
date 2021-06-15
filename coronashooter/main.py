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
                           K_p
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
        self.screen_size = self.tela.get_size()
        pygame.mouse.set_visible(0)
        pygame.display.set_caption('Corona Shooter')
        self.run = True
        self.pause = False

    def manutenção(self):
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
            enemy = Virus([0, 0])
            size = enemy.get_size()
            enemy.set_pos([min(max(x, size[0] / 2), self.screen_size[0] - size[0] / 2), size[1] / 2])
            colisores = pygame.sprite.spritecollide(enemy, virii, False)
            if colisores:
                return
            self.elementos["virii"].add(enemy)

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
            return hitted

        elif isinstance(elemento, pygame.sprite.Sprite):
            if pygame.sprite.spritecollide(elemento, list, 1):
                action()
            return elemento.morto

    def ação_elemento(self):
        self.verifica_impactos(self.jogador, self.elementos["tiros_inimigo"],
                               self.jogador.alvejado)
        if self.jogador.morto:
            self.run = False
            return

        # Verifica se o personagem trombou em algum inimigo
        self.verifica_impactos(self.jogador, self.elementos["virii"],
                               self.jogador.colisão)
        if self.jogador.morto:
            self.run = False
            return
        # Verifica se o personagem atingiu algum alvo.
        hitted = self.verifica_impactos(self.elementos["tiros"],
                                        self.elementos["virii"],
                                        Virus.alvejado)

        # Aumenta a pontos baseado no número de acertos:
        self.jogador.set_pontos(self.jogador.get_pontos() + len(hitted))

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
        self.tela.blit(vidas,(0,0))
        self.tela.blit(pontuacao,(550,0))
        self.tela.blit(nivel,(300,0))

    def tela_inicial(self, dt):
        fonte_grande =  pygame.font.SysFont("comicsansms", 70)
        fonte_pequena =  pygame.font.SysFont("comicsansms", 30)
        
        mensagem_inicio = fonte_grande.render('Coronashooter',True, (255, 255, 255))
        mensagem_começar = fonte_pequena.render('Pressione Qualquer Tecla',True, (255, 255, 255))
        
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
            pygame.display.flip()
            
    def muda_pause(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_p:
                self.pause = False

    def game_over(self):
        over = True
        imagem_fundo = pygame.image.load('./imagens/game-over.jpeg').convert()
        imagem_fundo =  pygame.transform.scale(imagem_fundo, self.tela.get_size())
        while over:
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
            pygame.display.flip()
    
    def loop(self):
        dt = 16
        self.tela_inicial(dt)
        
        while True:
            clock = pygame.time.Clock()
            self.elementos['virii'] = pygame.sprite.RenderPlain(Virus([120, 50]))
            self.jogador = Jogador([200, 400], 5)
            self.elementos['jogador'] = pygame.sprite.RenderPlain(self.jogador)
            self.elementos['tiros'] = pygame.sprite.RenderPlain()
            self.elementos['tiros_inimigo'] = pygame.sprite.RenderPlain()
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
                    pygame.display.flip()
                else:
                    self.muda_pause()
                  
            if self.jogador.morto:
                self.game_over()
                J.__init__() # Reinicia valores para o novo jogo
            else:
                pygame.quit()
                sys.exit()
                break


class Nave(ElementoSprite):
    def __init__(self, position, lives=0, speed=[0, 0], image=None, new_size=[83, 248]):
        self.acceleration = [6, 6]
        if not image:
            image = "seringa.png"
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
        if self.pontos > 100: l = 3
        if self.pontos > 300: l = 5

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


if __name__ == '__main__':
        J = Jogo()
        J.loop()