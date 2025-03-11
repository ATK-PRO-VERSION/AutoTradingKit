from PySide6.QtCore import Signal, Qt, QSize, QPoint
from PySide6.QtWidgets import QWidget


from atklip.gui.components.scroll_interface import ScrollInterface
from atklip.gui.qfluentwidgets import *
from atklip.gui.qfluentwidgets.common.icon import FluentIcon as FIF
from atklip.gui import qconfig, Config

class _SplitDropButton(SplitDropButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""QToolButton {
                            border: none;
                            border-radius: 4px;
                            background-color: transparent;}""")
    def enterEvent(self, event):
        background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        self.setStyleSheet(f"""QToolButton {{
                                    border: none;
                                    border-radius: 4px;
                                    background-color: {background_color};}}""")
        super().enterEvent(event)
    def leaveEvent(self, event):
        self.setStyleSheet("""QToolButton {
                                    border: none;
                                    border-radius: 4px;
                                    background-color: transparent;}""")
        super().leaveEvent(event)


class _TitleLabel(TitleLabel):
    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)
        color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.set_stylesheet(color)
        self.setFixedHeight(35)
        self.setMinimumWidth(120)
        self.setContentsMargins(0,0,0,0)

    def set_text(self,text,color):
        self.setText(text)
        self.set_stylesheet(color)
    def title(self):
        return self.text()
    def set_stylesheet(self,color):
        self.setStyleSheet(f"""QLabel {{
                            background-color: transparent;
                            border: none;
                            border-radius: 4px;
                            color: {color};
                            font: 12pt "Segoe UI" 'PingFang SC';
                            font-weight: SemiBold;
                        }}""")
    # def enterEvent(self, event):
    #     background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
    #     if self.isChecked():
    #         color = "#0055ff"
    #     else:
    #         color = "#d1d4dc" if isDarkTheme() else  "#161616"
    #     self.setStyleSheet(f"""QPushButton {{
    #         background-color: {background_color};
    #         border: none;
    #         border-radius: 4px;
    #         color: {color};
    #         font: 12pt "Segoe UI";
    #         font-weight: Bold;
    #         }}""")

    #     super().enterEvent(event)
    # def leaveEvent(self, event):
    #     #background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
    #     if self.isChecked():
    #         color = "#0055ff"
    #     else:
    #         color = "#d1d4dc" if isDarkTheme() else  "#161616"
    #     self.set_stylesheet(color)
    #     super().leaveEvent(event)


class LayoutButton(SplitWidgetBase):

    clicked = Signal()
    #@singledispatchmethod
    def __init__(self, parent: QWidget = None):
        super().__init__(parent=parent)
        self.setObjectName('IndicatorButton')

        self.cfg:Config = qconfig._cfg

        self.titleLabel:_TitleLabel = _TitleLabel("ATK main layout",self)

        self.setWidget(self.titleLabel)
        #self.indicator.show()
        self.setDropButton(_SplitDropButton(self))
        self.setDropIcon(FIF.ARROW_DOWN)
        self.setDropIconSize(QSize(10, 10))
        self.dropButton.setFixedSize(16,30)
        self._postInit()

    def get_current_inteval(self):
        return self.current_active.title()

    def save_favorites(self):
        if self.favorites != []:
            for item in  self.favorites:
                pass
    def setWidget(self, widget: QWidget):
        """ set the widget on left side """

        self.hBoxLayout.insertWidget(0, widget, 1, Qt.AlignLeft)

    def uncheck_items(self,btn):
        pass
    def set_text_color(self):
        pass
        # btn = self.sender()
        # if btn.isChecked():
        #     self.uncheck_items(btn)
        #     btn.setStyleSheet("""QPushButton {
        #             background-color: transparent;
        #             border: none;
        #             border-radius: 4px;
        #             margin: 0;
        #             color: "#0055ff";
        #             font: 15px 'Segoe UI', 'PingFang SC',  'Arial';
        #             font-weight: Bold;
        #             }""")

    def _postInit(self):
        pass
        
    
    def setcurrent_item(self,current_active):
        pass

    def setFlyout(self, flyout):
        self.flyout = flyout
    def showFlyout(self):
        """ show flyout """
        w = self.flyout
        if not w:
            return
        if isinstance(w, RoundMenu):
            #w.view.setMinimumWidth(self.width())
            #w.view.adjustSize()
            #w.adjustSize()
            x = self.width()
            #y = self.height()
            y = 0
            w.exec(self.mapToGlobal(QPoint(x, y)))
    
    def add_remove_to_favorites(self, title:str=None):
        """ add item to favorites """
        pass
    def change_item(self, title:str=None):
        """ change item """
        pass



from typing import Union
from atklip.gui.components.readme import ReadmeViewer
from atklip.gui.qfluentwidgets.components import HWIDGET
from atklip.gui.components._pushbutton import IconTextChangeButton


from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QIcon, QColor
from PySide6.QtWidgets import QSizePolicy, QWidget, QHBoxLayout

from atklip.gui.qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit, PushButton, CaptionLabel, setTheme, Theme


class LinkSponsor(MessageBoxBase):
    """ Custom message box """

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.ScrollInterface = ScrollInterface(self)
        self.ScrollInterface.setSpacing(6)
        self.ScrollInterface.setContentsMargins(1,1,1,1)
        
        text = """   Support ATK Development and Help Us Grow!

    Dear ATK Users and Supporters,
    
    ATK has been a valuable tool for many of you, helping to streamline workflows, solve problems, and improve productivity. However, maintaining and improving ATK requires significant resources, especially as we work to develop new features, fix bugs, and ensure the project remains sustainable for the long term.
To continue delivering the best experience for our users, we need your support. Your sponsorship will directly fund:

    * Development of new features** outlined in our Roadmap, ensuring ATK evolves to meet your needs.
    * Bug fixes and optimizations** to keep ATK stable, reliable, and efficient.
    * Support for our developers** , who work tirelessly to make ATK better every day.

    Why Sponsor ATK?

    * If ATK has helped you in your work or personal projects, your contribution ensures it can continue to do so for others.
    * Your support allows us to prioritize features and improvements that matter most to the community.
    * Sponsoring ATK is an investment in a tool you already rely on, ensuring its growth and sustainability.

    How You Can Help:

    * Click the link below to sponsor ATK via PayPal. Every contribution, no matter the size, makes a difference.
    * You can sent to me a gift via my bank account (Vietnamese Bank), it is shown below
    * Share this message with others who benefit from ATK. The more support we receive, the faster we can deliver new features and improvements.

    Thank You for Your Support!
    Your generosity and belief in ATK mean the world to us. Together, we can make ATK even better and ensure it remains a powerful tool for everyone who depends on it.

    With gratitude,
    mr.BigD - Creator/Developer of ATK"""

        title = StrongBodyLabel(text,self)
        
        bank_tt = SubtitleLabel('1. You can support me via Vietnamese bank account 👇️', self)
        # bank_tt.setStyleSheet("color:#f359c9;")
        bank_acc = SubtitleLabel('MB Bank: 8699991689999 | PHAM CONG CHE |', self)
        
        paypal = SubtitleLabel('2. You can subscribe or sponsor via Paypal 👇️', self)
        # paypal.setStyleSheet("color:#f359c9;")
        self.payment_4 = HyperlinkButton('https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=XTHUBP3TB5H7J', 'Paypal sponsor 5$', self, FluentIcon.LINK)
        self.payment_5 = HyperlinkButton('https://www.paypal.com/ncp/payment/G9R3YNN89KR8Y', 'Paypal sponsor 10$', self, FluentIcon.LINK)
        self.payment_6 = HyperlinkButton('https://www.paypal.com/ncp/payment/363TPLRF4NAF4', 'Paypal sponsor 20$', self, FluentIcon.LINK)
        
        
        self.payment_1 = HyperlinkButton('https://www.paypal.com/webapps/billing/plans/subscribe?plan_id=P-0F53588022198101GM63BMVA', 'Paypal subscribe 10$/month', self, FluentIcon.LINK)
        self.payment_2 = HyperlinkButton('https://www.paypal.com/webapps/billing/plans/subscribe?plan_id=P-06E5757414542143MM63BSGI', 'Paypal subscribe 20$/month', self, FluentIcon.LINK)
        self.payment_3 = HyperlinkButton('https://www.paypal.com/webapps/billing/plans/subscribe?plan_id=P-00V92834XG336831FM63BTEQ', 'Paypal subscribe 50$/month', self, FluentIcon.LINK)
        
        
        label = SubtitleLabel(self.tr('3. You also sent some gift to me via binace transfer 👇️'), self)
        # label.setStyleSheet("color:#f359c9;")
        image_path:str = get_real_path("atklip/appdata/1739980400330.png")
        self.imageLabel = ImageLabel(image_path)
        self.imageLabel.scaledToWidth(1000)
        self.imageLabel.scaledToHeight(400)
        self.imageLabel.setBorderRadius(2, 2, 2, 2)

        w= self.width()
        
        
        self.ScrollInterface.addWidget(title, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(HorizontalSeparator(self,w=w,h=20))
        
        self.ScrollInterface.addWidget(bank_tt, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(bank_acc, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(HorizontalSeparator(self,w=w,h=20))
        
        # add widget to view layout
        self.ScrollInterface.addWidget(paypal)
        
        self.ScrollInterface.addWidget(self.payment_1, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(self.payment_2, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(self.payment_3, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(self.payment_4, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(self.payment_5, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(self.payment_6, 0, Qt.AlignLeft)
        
        self.ScrollInterface.addWidget(HorizontalSeparator(self,w=w,h=20))
        
        self.ScrollInterface.addWidget(label, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(self.imageLabel, 0, Qt.AlignLeft)
        
        self.ScrollInterface.addWidget(HorizontalSeparator(self,w=w,h=20))
        
        Youtube_Chanel = HyperlinkButton('https://www.youtube.com/@AutoTradingKit', 'Youtube Chanel', self, FluentIcon.LINK)
        Facebook = HyperlinkButton('https://www.facebook.com/che.linh.9096/', "Author's Facebook", self, FluentIcon.LINK)
        Discord = HyperlinkButton('https://discord.gg/UNDh5MyR', 'Discord', self, FluentIcon.LINK)
        ATK_Facebook_Group = HyperlinkButton('https://www.facebook.com/groups/748831980507126', 'ATK Facebook Group', self, FluentIcon.LINK)
        github = HyperlinkButton('https://github.com/Khanhlinhdang/AutoTradingKit-Pro', "ATK's github repository", self, FluentIcon.LINK)
        
        infor = """ Authors and acknowledgment
        
    Pham Cong Che (nickname: BigD) - A trader, a freelancer and a developer from Viet Nam. The author of ATK.
    Email: khanhlinhdangthditrach@gmail.com
    Skype: khanhlinhdangthditrach@gmail.com
    Zalo: 0343845888
    Telegram: +79921849116 or username : @Chelinh0308"""
        infor_title = StrongBodyLabel(infor,self)
        self.ScrollInterface.addWidget(infor_title, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(HorizontalSeparator(self,w=w,h=20))
        self.ScrollInterface.addWidget(Youtube_Chanel, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(Facebook, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(Discord, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(ATK_Facebook_Group, 0, Qt.AlignLeft)
        self.ScrollInterface.addWidget(github, 0, Qt.AlignLeft)
        
        
        self.viewLayout.addWidget(self.ScrollInterface)
        
        # change the text of button
        self.yesButton.setText('Done')
        self.cancelButton.setText('Close')

        self.widget.setMinimumWidth(1100)
        self.widget.setMinimumHeight(600)
        # self.hideYesButton()



class DonateBtn(HWIDGET):
    clicked = Signal()
    def __init__(self,text="Sponsor",parent:QWidget=None):
        super().__init__(parent)
        self.parent = parent
        self.setContentsMargins(0,0,0,0)
        self.setFixedHeight(35)
        self.btn = IconTextChangeButton(icon=FIF.SPONSOR,text=text,parent=self)
        self.btn.set_sponsor()
        self.addWidget(self.btn)
        self.btn.clicked.connect(self.showDialog)
    
    
    def showDialog(self):
        w = LinkSponsor(self.parent)
        if w.exec():
            w.deleteLater()
    
