import tkinter as tk
class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y, speed=7):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = speed
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                   x + self.radius, y + self.radius,
                                   fill='black')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100
        self.height = 10
        self.speed = 40  
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='purple')
        super(Paddle, self).__init__(canvas, item)

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)

    def move_left(self):
        self.move(-self.speed)

    def move_right(self):
        self.move(self.speed)


class Brick(GameObject):
    COLORS = {
        1: 'lightblue',
        2: 'blue',
        3: 'darkblue'
    }

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 5
        self.score = 0
        self.level = 1
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='lightgrey',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.balls = []
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle
        self.create_bricks()

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move_left())
        self.canvas.bind('<Right>', lambda _: self.paddle.move_right())
        self.canvas.bind('<space>', self.start_game)

    def create_bricks(self):
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

    def setup_game(self):
        self.add_initial_ball()  
        self.update_lives_text()
        self.update_score_text()
        self.text = self.draw_text(300, 200,
                                    'Press Space to start', size='30')

    def add_initial_ball(self):
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        ball = Ball(self.canvas, x, 310)
        self.balls.append(ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Helvetica', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font, fill='purple')

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def update_score_text(self):
        text = 'Score: %s  Level: %s' % (self.score, self.level)
        if hasattr(self, 'score_hud'):
            self.canvas.itemconfig(self.score_hud, text=text)
        else:
            self.score_hud = self.draw_text(500, 20, text, 15)

    def start_game(self, event=None):
        if self.lives < 0:
            return
        
        self.canvas.delete(self.text)
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0: 
            self.level += 1
            self.increase_ball_speed()  # Meningkatkan kecepatan bola setiap level
            self.create_bricks()
            self.draw_text(300, 200, f'Congratulations! Score: {self.score}', size='24')
        else:
            for ball in self.balls:
                ball.update()
            self.after(30, self.game_loop)

    def check_collisions(self):
        for ball in self.balls:
            ball_coords = ball.get_position()
            items = self.canvas.find_overlapping(*ball_coords)
            objects = [self.items[x] for x in items if x in self.items]
            ball.collide(objects)

            if ball_coords[3] >= self.height:  
                self.lives -= 1
                self.balls.remove(ball)
                ball.delete()
                if self.lives >= 0:
                    self.ensure_one_ball()  
                else:
                    self.display_game_over()  # Tampilkan pesan Game Over

        self.update_lives_text()
        
        for game_object in objects:
            if isinstance(game_object, Brick):
                self.score += 10
                self.update_score_text()
                if self.score % 50 == 0:  # Menaikkan level setiap 50 poin
                    self.level += 1
                    self.increase_ball_speed()  # Meningkatkan kecepatan bola setiap level
                    self.update_score_text()

    def ensure_one_ball(self):
        if len(self.balls) == 0:
            self.add_initial_ball()  # Menambahkan bola baru jika tidak ada bola

    def increase_ball_speed(self):
        for ball in self.balls:
            ball.speed += 2  # Meningkatkan kecepatan bola

    def display_game_over(self):
        self.draw_text(300, 200, f'Congratulations! Score: {self.score}', size='24')
        self.canvas.unbind('<Left>')
        self.canvas.unbind('<Right>')
        # Menghentikan permainan dengan tidak memanggil game_loop lagi

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()