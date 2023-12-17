/*
const express = require("express");
const multer = require("multer");

const { uploadImage } = require("../controllers/image");
const { isLoggedIn } = require("../middlewares");

const router = express.Router();

const upload = multer({
  storage: multerS3({
    s3,
    bucket: "nodebirdhanseul",
    key(req, file, cb) {
      cb(null, `original/${Date.now()}_${file.originalname}`);
    },
  }),
  limits: { fileSize: 10 * 1024 * 1024 },
});

router.post("/img", isLoggedIn, upload.single("img"), afterUploadImage);

module.exports = router;
*/
