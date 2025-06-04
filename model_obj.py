from PySide6.QtCore import QObject, Signal
import os
from config import UI_ONLY
if not UI_ONLY:
    import tensorflow as tf
    from keras.saving import register_keras_serializable

if not UI_ONLY:
    @register_keras_serializable()
    class AntipodalConstraint(tf.keras.constraints.Constraint):
        def __call__(self, w):
            return tf.sign(w)  # Forces weights to -1 or 1

class model(QObject):
    modelChanged = Signal()
    def __init__(self,name):
        super().__init__()
        if name == "None":
            self.name = name
            self.input_size = 256
            self.SM_size = None
            self.SR = None
            self.SM = None
        else:
            if UI_ONLY:
                self.name = name
                self.input_size = 256
                self.SM_size = None
                self.SR = None
                self.SM = None
            else:
                self.name = name
                formatted = self.name +".keras"
                path  = os.path.join(os.path.dirname(os.path.abspath(__file__)),"__models",formatted)
                self.keras_model = tf.keras.models.load_model(path, custom_objects={"AntipodalConstraint": AntipodalConstraint})
                if self.keras_model.name == "MFFSE":
                    self.input_size = self.keras_model.input_shape[1]
                    self.SM = self.keras_model.layers[2].weights[0].numpy().T
                    self.SM_size = self.SM.shape
                    self.SR = float(self.SM_size[0]/self.SM_size[1])
                    
                else:
                    raise ValueError("Model is not MFFSE model type")
                

    def setModel(self, other_model):
        self.name = other_model.name
        self.input_size = other_model.input_size
        self.SM_size = other_model.SM_size
        self.SR = other_model.SR
        self.SM = other_model.SM
        self.modelChanged.emit()