const express = require("express");
const multer = require("multer");

const { uploadSource } = require("../controllers/source");
//const { isLoggedIn } = require("../middlewares");

const router = express.Router();

router.post("/source", uploadSource);

module.exports = router;