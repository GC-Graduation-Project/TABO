/*
const express = require("express");
const passport = require("passport");

const { isLoggedIn, isNotLoggedIn } = require("../middlewares");
const { join, login, logout } = require("../controllers/auth");

const router = express.Router();

router.post("/join", isNotLoggedIn, join);
router.post("/login", isNotLoggedIn, login);
router.get("/logout", isLoggedIn, logout);

// /auth/kakao -> 카카오 로그인 화면 -> /auth/kakao/callback
//GET /auth/kakao
router.get("/kakao", passport.authenticate("kakao"));

//GET /auth/kakao/callback
router.get(
  "/kakao/callback",
  passport.authenticate("kakao", {
    failureRedirect: "/?loginError=카카오로그인 실패",
  }),
  (req, res) => {
    res.redirect("/"); //성공 시에는 /로 이동
  }
);

module.exports = router;
*/
