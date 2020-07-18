# cg_playground
A project where I can play around with computer graphics a little bit.
My idea is to implement a series of small projects inside this one as I slowly 
progress through computer graphics topics.

## Tiny renderer
I'm implementing my own version of [this](https://github.com/ssloy/tinyrenderer/wiki) great tutorial, the idea is
to implement a renderer step-by-step: implement line drawing, then .obj parsing, then wireframe rendering and so on.
Here's a video with my progress so far:


[![](http://img.youtube.com/vi/yxCV73AJJt8/0.jpg)](http://www.youtube.com/watch?v=yxCV73AJJt8 "Click to play on Youtube")

## Trying it out
This project uses [Miniconda](https://docs.conda.io/en/latest/miniconda.html) as a package manager
and [conda devenv](https://github.com/ESSS/conda-devenv). After installing `Miniconda` you need
to install `conda-devenv` on your `base` (root environment) with:
```bash
conda activate base 
conda install conda-devenv
conda deactivate
```
Then in order to create the environment run
```bash
conda devenv
```
on the root of this project.