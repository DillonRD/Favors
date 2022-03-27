const router = require('express').Router();
const { User, Post } = require('../models');
const sequelize = require('../config/connection');
const withAuth = require('../utils/auth'); //redirect to login if not logged in

router.get('/', withAuth, async (req, res) => {
  Post.findAll({
    attributes: [
      'id',
      'title',
      'created_at',
      'post_content'
    ],
    include: [
      {
        model: User,
        attributes: ['email']
      }
    ]
  })
    .then(dbPostData => {
      const posts = dbPostData.map(post => post.get({ plain: true })); //posts is referred here on partials
      res.render('home', {
          posts,
          loggedIn: req.session.loggedIn,
        });
    })
    .catch(err => {
      console.log(err);
      res.status(500).json(err);
    });
  });

  router.get('/login', (req, res) => {
    if (req.session.loggedIn) {
      res.redirect('/');
      return;
    }
  
    res.render('login');
  });

  
  router.get('/signup', (req, res) => {
    if (req.session.loggedIn) {
      res.redirect('/');
      return;
    }
  
    res.render('signup');
  });

  router.get('/post/:id', (req, res) => {
    Post.findOne({
      where: {
        id: req.params.id
      },
      attributes: [
        'id',
        'title',
        'created_at',
        'post_content'
      ],
      include: [
        {
          model: User,
          attributes: ['email']
        }
      ]
    })
      .then(dbPostData => {
        if (!dbPostData) {
          res.status(404).json({ message: 'Error' });
          return;
        }
  

        const post = dbPostData.get({ plain: true });

        res.render('singlePost', {
            post,
            loggedIn: req.session.loggedIn
          });
      })
      .catch(err => {
        console.log(err);
        res.status(500).json(err);
      });
});

  


module.exports = router;