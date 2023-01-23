import pygame

class Button():
    def __init__(self, x: int, y: int, image: pygame.Surface) -> None:
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x,y)

    def draw(self, screen: pygame.Surface):
        action = False

        #get mouse postion
        pos = pygame.mouse.get_pos()

        #check mouse over and clicked
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]:
                action = True

        screen.blit(self.image, self.rect)

        return action