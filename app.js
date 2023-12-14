import express from 'express';
import { fileURLToPath } from "url";   
import cors from 'cors'
import puppeteer from 'puppeteer';
import fs from 'fs'

//dir_name 을 사용하기 위함
const __dirname = fileURLToPath(new URL(".", import.meta.url)); 
// const __filename = fileURLToPath(import.meta.url); 

const app = express();

app.use(cors({
  origin: "http://localhost:3000", // 접근 권한을 부여하는 도메인
  credentials: true, // 응답 헤더에 Access-Control-Allow-Credentials 추가
  optionsSuccessStatus: 200, // 응답 상태 200으로 설정
}));


//req.body 사용하기 위한 bodyParser
app.use(express.text({type: "text/plain"}));

//포트 설정
app.set('port', process.env.PORT || 3000);

//브라우저에서 필요한 js 파일들을 사용할수 있게 해줌
app.use('/load.js', express.static(__dirname+'/load.js'));
app.use('/main.dev.js', express.static(__dirname+'/main.dev.js'));
app.use('/jspdf',express.static(__dirname+'/node_modules/'))

app.get('/vextabhtml',(req,res)=> {
        res.sendFile(__dirname+"/load.html")
})

app.post("/getSVG",(req,res)=>{

    (async () => {

        const notedata = req.body
        
        console.log("frombody",notedata)
        const browser = await puppeteer.launch({headless: "new"});
        const page = await browser.newPage();
        await page.goto("http://localhost:3000/vextabhtml")
        page.on('console', (msg) => console.log('페이지 로그:', msg.text()));

        const target = page.$("target")

        const result = await page.evaluate(async(notedata,target)=> {
          await new Promise(resolve=> setTimeout(resolve,5000))
          // console.log('추가스크립트')
          const {renderSvg,vextab} = await import('./load.js')
           var isRendered = renderSvg(vextab,notedata,target)
        console.log("랜더링중")
        new Promise(page => setTimeout(page, 5000));

        if(isRendered)
        {
          console.log('랜더링 완료');
        }else{
          console.log("랜더링 실패 (vextab error)");
          
        }

        return isRendered

        },notedata,target)


        // console.log(result)
       if(result) {
              // Get the bounding box of the div
          const divBoundingBox = await page.$eval('#target', (div) => {
          console.log(div.childNodes[0])
          console.log("스캔하는중..")
          const { x, y, width, height } = div.getBoundingClientRect();
          return { x, y, width, height };
  });

  // Capture the screenshot of the div
  await page.screenshot({
    path: 'div_screenshot.png',
    clip: {
      x: divBoundingBox.x,
      y: divBoundingBox.y,
      width: divBoundingBox.width,
      height: divBoundingBox.height
    }
  },console.log("스캔완료"));
  
  const imagePath = 'div_screenshot.png';

  // 이미지를 읽어서 전송
  fs.readFile(imagePath, (err, data) => {
    if (err) {
      console.error(err);
      res.status(500).send('Internal Server Error');
      return;
    }

    // 이미지 전송
    res.writeHead(200, { 'Content-Type': 'image/jpeg' });
    res.end(data);
  });

  }else {

        console.log("render failed")
        res.send("Rendering faild. check your note data is correct or find out what occurred the error")

       }
       await browser.close()
      })();

})

app.get('/', (req, res) => {
    res.send('Hello, Express')
});


app.listen(app.get('port'), ()=>{
    console.log(app.get('port'), '번 포트에서 대기 중')
});


