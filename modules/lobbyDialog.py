"""
This module contains the LobbyDialog class, which is used to create a dialog box for creating a lobby.
"""
import pygame
from time import time
from modules.colours import *

class LobbyDialog:
    """
    Class to create a dialog box for creating a lobby.
    """
    def __init__(self, game_modes, submitFunction, marginLeft=25, width=300, height=500):
        self.submitFunction = submitFunction
        self.screen = pygame.display.set_mode((width, height))
        self.WIDTH = width
        self.HEIGHT = height
        self.marginLeft = marginLeft
        self.font = pygame.font.Font(None, 36)
        self.label_font = pygame.font.Font(None, 28)

        # Lobby dialog title
        self.title_font = pygame.font.Font(None, 48)
        self.title_text = self.title_font.render("Create a Lobby", True, WHITE)

        # Lobby name input box
        self.input_box = pygame.Rect(self.marginLeft, 110, 250, 36)
        self.lobby_name = ''
        self.is_public = True

        # Game mode dropdown
        self.drop_down_rect = pygame.Rect(self.marginLeft, 200, 250, 36)
        self.selected_game_mode = game_modes[0]
        self.game_modes = game_modes
        self.drop_down_open = False

        # Visibility button
        self.toggle_rect = pygame.Rect(self.marginLeft, 290, 100, 36)

        # Submit button
        self.submit_font = pygame.font.Font(None, 38)
        self.submit_button_rect = pygame.Rect(self.WIDTH // 2 - 150//2, self.HEIGHT - 60, 150, 40)

        self.cursor_visible = True
        self.cursor_last_blink = time()
        self.inputActive = False
        self.hovering_input = False
        self.hovering_dropdown = False
        self.hovering_dropdown_option = None
        self.hovering_toggle = False  
        self.hovering_submit = False  

    def draw_label(self, text, position, font=None):
        """Helper function to draw labels above each input box."""
        if font is None:
            font = self.label_font
        label_surface = self.font.render(text, True, WHITE)
        self.screen.blit(label_surface, position)

    def draw_input_box(self):
        self.draw_label("Lobby Name", (self.input_box.x, self.input_box.y - 30))

        # Highlight the input box if hovered
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOUR if self.hovering_input else WHITE, self.input_box, 2)
        text_surface = self.font.render(self.lobby_name, True, WHITE)
        self.screen.blit(text_surface, (self.input_box.x + 5, self.input_box.y + 5))
        self.input_box.w = max(self.input_box.width, text_surface.get_width() + 10)

        # Cursor blinking effect
        current_time = time()
        if current_time - self.cursor_last_blink >= 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_last_blink = current_time

        if self.inputActive and self.cursor_visible:
            cursor_x = self.input_box.x + 5 + text_surface.get_width() + 2
            cursor_y = self.input_box.y + 5
            pygame.draw.line(self.screen, WHITE, (cursor_x, cursor_y), (cursor_x, cursor_y + 26), 2)

    def draw_toggle_button(self):
        self.draw_label("Visibility", (self.toggle_rect.x, self.toggle_rect.y - 30))

        # Determine text color based on the visibility state
        label = "Public" if self.is_public else "Private"
        text_color = (0, 255, 0) if self.is_public else (255, 0, 0)

        pygame.draw.rect(self.screen, BLACK, self.toggle_rect)

        text_surface = self.font.render(label, True, text_color)
        self.screen.blit(text_surface, (self.toggle_rect.x + self.toggle_rect.width // 2 - text_surface.get_width() // 2, self.toggle_rect.y + 5))

        # Draw the border, highlight if hovering
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOUR if self.hovering_toggle else WHITE, self.toggle_rect, 2)

    def draw_submit_button(self):
        # Draw the submit button
        pygame.draw.rect(self.screen, HIGHLIGHT_COLOUR if self.hovering_submit else WHITE, self.submit_button_rect, 2)
        text_surface = self.submit_font.render("Submit", True, WHITE)
        self.screen.blit(text_surface, (self.submit_button_rect.x + self.submit_button_rect.width // 2 - text_surface.get_width() // 2, self.submit_button_rect.y + 8))

    def draw_drop_down(self):
        # Label for the dropdown
        self.draw_label("Mode", (self.drop_down_rect.x, self.drop_down_rect.y - 30))

        pygame.draw.rect(self.screen, HIGHLIGHT_COLOUR if self.hovering_dropdown else WHITE, self.drop_down_rect, 2)
        mode_text = self.font.render(self.selected_game_mode, True, WHITE)
        self.screen.blit(mode_text, (self.drop_down_rect.x + 5, self.drop_down_rect.y + 5))

        if self.drop_down_open:
            dropdown_height = len(self.game_modes) * 40
            pygame.draw.rect(self.screen, BLACK, (self.drop_down_rect.x, self.drop_down_rect.y + 36, self.drop_down_rect.w, dropdown_height))

            for i, mode in enumerate(self.game_modes):
                option_rect = pygame.Rect(self.drop_down_rect.x, self.drop_down_rect.y + (i + 1) * 40, self.drop_down_rect.w, 36)

                # Highlight option if hovered
                if i == self.hovering_dropdown_option:
                    pygame.draw.rect(self.screen, HIGHLIGHT_COLOUR, option_rect)
                else:
                    pygame.draw.rect(self.screen, GREY, option_rect)

                option_text = self.font.render(mode, True, WHITE)
                self.screen.blit(option_text, (option_rect.x + 5, option_rect.y + 5))

    def setHighlights(self, mouse_pos):
        # Check mouse hover
        self.hovering_input = self.input_box.collidepoint(mouse_pos)

        self.hovering_dropdown = self.drop_down_rect.collidepoint(mouse_pos)

        self.hovering_toggle = self.toggle_rect.collidepoint(mouse_pos)

        self.hovering_submit = self.submit_button_rect.collidepoint(mouse_pos)

        if self.drop_down_open:
            self.hovering_dropdown_option = None
            for i in range(len(self.game_modes)):
                option_rect = pygame.Rect(self.drop_down_rect.x, self.drop_down_rect.y + (i + 1) * 40, self.drop_down_rect.w, 36)
                if option_rect.collidepoint(mouse_pos):
                    self.hovering_dropdown_option = i
                    break

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle public/private
            if self.toggle_rect.collidepoint(event.pos):
                self.is_public = not self.is_public

            # Handle dropdown
            if self.drop_down_rect.collidepoint(event.pos):
                self.drop_down_open = not self.drop_down_open
            elif self.drop_down_open and self.hovering_dropdown_option is not None:
                # If an option is clicked, select the game mode
                self.selected_game_mode = self.game_modes[self.hovering_dropdown_option]
                self.drop_down_open = False

            # Check input box
            if self.input_box.collidepoint(event.pos):
                self.inputActive = not self.inputActive
            else:
                self.inputActive = False

            # Handle submit button click
            if self.submit_button_rect.collidepoint(event.pos):
                print(f"Lobby Name: {self.lobby_name}, Public: {self.is_public}, Game Mode: {self.selected_game_mode}")
                self.running = False
                self.submitFunction({
                    'lobby':self.lobby_name,
                    'public':self.is_public,
                    'mode':self.selected_game_mode
                })

        if event.type == pygame.KEYDOWN:
            if self.inputActive:
                if event.key == pygame.K_RETURN:
                    print(f"Lobby Name: {self.lobby_name}, Public: {self.is_public}, Game Mode: {self.selected_game_mode}")
                elif event.key == pygame.K_BACKSPACE:
                    self.lobby_name = self.lobby_name[:-1]
                else:
                    self.lobby_name += event.unicode

    def run_dialog(self):
        clock = pygame.time.Clock()
        self.running = True
        while self.running:
            self.screen.fill(BLACK)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.handle_events(event)

            self.screen.blit(self.title_text, (self.WIDTH // 2 - self.title_text.get_width() // 2, 20))

            self.setHighlights(pygame.mouse.get_pos())
            self.draw_input_box()
            self.draw_toggle_button()
            self.draw_drop_down()
            self.draw_submit_button()

            pygame.display.flip()
            clock.tick(30)