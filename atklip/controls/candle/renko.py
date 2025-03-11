class Renko:
    def __init__(self, start_price=None):
        self.bricks = []
        self.current_direction = 0
        self.brick_end_price = start_price
        self.pwick = 0   # positive wick
        self.nwick = 0   # negative wick
        self.brick_num = 0
        self.value = None
        
    def _create_brick(self, direction, brick_size, price):
        self.brick_end_price = round(self.brick_end_price + direction*brick_size,2)
        brick = {
            'direction': direction,
            'brick_num': self.brick_num,
            'wick_size': self.nwick if direction==1 else self.pwick,
            'brick_size': brick_size,
            'brick_end_price': self.brick_end_price,
            'price': price
        }
        self.bricks.append(brick)
        self.brick_num += 1
        self.current_direction = direction
        self.pwick = 0
        self.nwick = 0
        return brick        
        
    def update(self, price, brick_size):
        if(self.brick_end_price is None):
            self.brick_end_price = price
            #print("renko brick start price:", price)
            return None
        if(brick_size is None): return None
        bricks = None
        change = round(price - self.brick_end_price, 2)
        self.pwick = max(change, self.pwick)
        self.nwick = min(-change, self.nwick)
        if(self.current_direction == 0):
            direction = 0
            if(change >= brick_size): direction = 1
            elif(-change >= brick_size): direction = -1
            if(direction != 0):
                #print("firect brick direction:", str(direction))
                num_bricks = int(abs(change)//brick_size)
                bricks = [self._create_brick(direction, brick_size, price) for i in range(num_bricks)]
                
        elif(self.current_direction == 1):
            if(change >= brick_size):
                # more bricks in +1 direction
                num_bricks = int(abs(change)//brick_size)
                bricks = [self._create_brick(1, brick_size, price) for i in range(num_bricks)]
                
            elif(-change >= 2*brick_size):
                # reverse direction to -1
                num_bricks = int(abs(change)//brick_size)
                bricks = [self._create_brick(-1, brick_size, price) for i in range(num_bricks-1)]
                
        elif(self.current_direction == -1):
            if(-change >= brick_size):
                # more bricks in -1 direction
                num_bricks = int(abs(change)//brick_size)
                bricks = [self._create_brick(-1, brick_size, price) for i in range(num_bricks)]
                
            elif(change >= 2*brick_size):
                # reverse direction to +1
                num_bricks = int(abs(change)//brick_size)
                bricks = [self._create_brick(1, brick_size, price) for i in range(num_bricks-1)]

        self.value = bricks
        return bricks