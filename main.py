from model import pdf2imgs, Model_Handler

if __name__ == "__main__":

    model = Model_Handler()

    model.forward(image_path="page-2.png", input_prompt= "Please extract all informations of candicate in the CV.")