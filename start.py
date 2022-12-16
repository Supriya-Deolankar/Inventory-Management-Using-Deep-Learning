import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import controller.userController as usrc
import av  
from PIL import Image
import torch
import numpy as np
import time

usrc.create()
@st.cache
def model():
    return torch.hub.load('ultralytics/yolov5', 'custom', path="best.pt",force_reload=True) 

model=model()
class VideoProcessor:
    def __init__(self):
        self.res=None
        self.confidence=0.5

    def getRes(self):
        #time.sleep(5)
        return self.res

    def recv(self, frame):
 
        model.conf=self.confidence
        img = frame.to_ndarray(format="bgr24")
        
        # vision processing
        flipped = img[:, ::-1, :]

        # model processing
        im_pil = Image.fromarray(flipped)
        results = model(im_pil, size=112)
        self.res=results
        bbox_img = np.array(results.render()[0])

        
        return av.VideoFrame.from_ndarray(bbox_img, format="bgr24")

st.title("Cold Drinks Inventory Management System")

with st.container():
    views=['📊Data','🖼️Image','📹Video']
    view_mode=st.selectbox(options=views,label='None')
    if view_mode=='📊Data':
        st.title('📊Data')

        table=usrc.read()
        st.table(table)
        count=usrc.count_drinks()
        st.table(count)

        if(st.download_button(label='Download',data=table.to_csv(),mime='text/csv')):
            st.write('Data is written successfully to CSV File.')
            
        if(st.button(label='Clear data')):
            usrc.clear()

    if view_mode=='🖼️Image':
            st.title("🖼️ Cold Drinks Detection Image")
            image=st.file_uploader('Image',type=['png','jpg','jpeg'])
            with st.sidebar:
                date = st.date_input('Date')
                confidence=st.slider('Confidence threshold',0.00,1.00,0.8)
            if image:
                model.conf=confidence
                img = np.array(Image.open(image))

                # model processing
                im_pil = Image.fromarray(img)
                results = model(im_pil, size=112)
                bbox_img = np.array(results.render()[0])
                st.image(bbox_img, caption=f"Processed image", use_column_width=True,)
                
                count = results.pandas().xyxy[0]['name'].value_counts()
                with st.sidebar:
                    count
                if(st.button('Store')):
                    for row in count.index:
                        usrc.insert(date,row,int(count[row]))
                    st.success('Successfully stored!', icon="✅")
    

    if view_mode=='📹Video':
            st.title('📹Cold Drinks detection video')

            with st.sidebar:
                date = st.date_input('Date')
                confidence=st.slider('Confidence threshold',0.00,1.00,0.5)

            RTC_CONFIGURATION = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
            
            webrtc_ctx = webrtc_streamer(
                key="webcam",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration=RTC_CONFIGURATION,
                media_stream_constraints={"video": True, "audio": False},
                video_processor_factory=VideoProcessor,
                async_processing=True,
            )
            if webrtc_ctx.state.playing:
                    webrtc_ctx.video_processor.confidence=confidence
            with st.sidebar:
                    empty=st.empty()
            store=st.button('Store')
            if webrtc_ctx.state.playing:
                while True:
                    if webrtc_ctx.video_processor:
                        result = webrtc_ctx.video_processor.getRes()
                        if result!= None:
                            count = result.pandas().xyxy[0]['name'].value_counts()
                            empty.write(count)
                            for row in count.index:
                                if store:
                                    usrc.insert(date,row,int(count[row]))
                                    st.success('Successfully stored!', icon="✅")
                                    time.sleep(5)
                    else:
                        break
                        
                        
            
            
            





