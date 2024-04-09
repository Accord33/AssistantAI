import flet as ft

def main(page: ft.Page):
    def position_fixation(e): #画面を最前面に固定する関数
        page.window_always_on_top = (
            False
            if page.window_always_on_top == True
            else True
        )
        page.update()
    
    page.window_always_on_top = True #最初の状態
    c = ft.Switch(label="画面を固定", on_change=position_fixation,value=True) #Switchの作成
    page.add(c) #ページに追加

ft.app(target=main) #ページに表示 