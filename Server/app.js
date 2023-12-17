const express = require("express");
const morgan = require("morgan");
const session = require("express-session");
const dotenv = require("dotenv");
const passport = require("passport");
const helmet = require("helmet");
const hpp = require("hpp");

dotenv.config();
const pageRouter = require("./routes/page");
const authRouter = require("./routes/auth");
const imageRouter = require("./routes/image");
const pictureRouter = require("./routes/picture");
const sourceRouter = require("./routes/source");
//const { sequelize } = require("./models");
//const passportConfig = require("./passport");

const app = express();
//passportConfig();
app.set("port", process.env.PORT || 8080);

app.use(express.json());
app.use(express.urlencoded({ extended: false }));

app.use("/", pageRouter);
//app.use("/auth", authRouter);
//app.use("/image", imageRouter);
//app.use("/picture", pictureRouter);
//app.use("/source", sourceRouter);

app.use((req, res, next) => {
  const error = new Error(`${req.method} ${req.url} 라우터가 없습니다.`);
  error.status = 404;
  logger.error(error.message);
  next(error);
});

app.use((err, req, res, next) => {
  res.locals.message = err.message;
  res.locals.error = process.env.NODE_ENV !== "production" ? err : {};
  res.status(err.status || 500);
  //res.render("error");
});

module.exports = app;
