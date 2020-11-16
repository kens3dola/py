import math, pygame

def rot_around(surf,img,base_x,base_y,img_offset_x,img_offset_y,deg):
    background_img = pygame.Surface(((img.get_width()+img_offset_x)*2,(img.get_width()+img_offset_x)*2))
    background_img.blit(img,(img_offset_x+int(background_img.get_width()/2),int(background_img.get_width()/2)+img_offset_y))
    original_size = (background_img.get_width(),background_img.get_height())
    rotated_img = pygame.transform.rotate(background_img,deg)
    x_inc = rotated_img.get_width()-original_size[0]
    y_inc = rotated_img.get_height()-original_size[1]
    rotated_img.set_colorkey((0,0,0))
    surf.blit(rotated_img,(base_x-int(original_size[0]/2)-int(x_inc/2),base_y-int(original_size[1]/2)-int(y_inc/2)))

def point_degrees(p_1,p_2):
    x = p_2[0]-p_1[0]
    y = p_2[1]-p_1[1]
    base_rotation = 0
    if x < 0:
        base_rotation = 180
    if x == 0:
        if y < 0:
            return 270
        else:
            return 90
    else:
        return math.degrees(math.atan(y/x)) + base_rotation
