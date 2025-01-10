from panda3d.core import Point3
from panda3d.core import AmbientLight, DirectionalLight
from direct.showbase.ShowBase import ShowBase
from direct.task import Task

class MyApp(ShowBase):
    def __init__(self):
        super().__init__()

        # Kamera açısını ayarlamak (başlangıçta kamera biraz yukarı ve yakın)
        self.camera.setPos(5, -5, 5)
        self.camera.lookAt(Point3(0, 0, 0))

        # 3D küp modelini oluşturuyoruz
        self.cube = self.loader.loadModel("models/box")
        self.cube.reparentTo(self.render)
        self.cube.setScale(1, 1, 1)  # Küpün boyutunu ayarlıyoruz
        self.cube.setPos(0, 0, 0)  # Küpün başlangıç pozisyonu

        # Küp döndürme hareketini başlatıyoruz
        self.rotation_speed = 45  # Küpün dönüş hızını ayarlıyoruz (derece/saniye)
        self.taskMgr.add(self.rotate_cube, "rotate_cube")

        # Işık ekleyelim
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor((0.5, 0.5, 0.5, 1))
        directional_light = DirectionalLight("directional_light")
        directional_light.setColor((1, 1, 1, 1))

        # Işığı sahneye ekleyelim
        self.render.setLight(self.render.attachNewNode(ambient_light))
        self.render.setLight(self.render.attachNewNode(directional_light))

    def rotate_cube(self, task):
        # Küpü her frame'de döndürüyoruz
        self.cube.setH(self.cube.getH() + self.rotation_speed * task.dt)  # Y ekseninde dönüş
        return Task.cont  # Görev devam etsin

app = MyApp()
app.run()
