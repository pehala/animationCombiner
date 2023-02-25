# Animation Combiner for Blender
This is a plugin for [Blender](https://www.blender.org/) (3.0+), which simplifies creating animation by combining simple ones through custom UI.

## Current capabilities
* Can import/export animation from [MESSIF](https://gitlab.fi.muni.cz/disa/public/messif) .data files (if you would like to add more formats, please create an issue)
* Combines multiple animation into one
* Can interpolate between different animations

## Limitations
* Currently only normalized animation are supported
* Only one format supported so far
* All animation needs to have same framerate

## Planned features
* More formats!
* Ability to apply animations only to a specific body parts
* More skeleton types and ability to interpolate between them
* Ability to work with multiple frame rates and export to a specific one

## Installation
* [Download the latest archive from releases](https://github.com/pehala/animationCombiner/releases/latest)
* Install plugin to Blender
  * **Edit** -> **Preferences** -> **Install**..
  * Search for "**animationCombiner**"
  * Enable plugin


## Usage
* Look into the right side of the viewport and switch to Animation tab
  * All UI elements are under one panel called **AnimationCombiner**
* Create new armature through **Create Armature** button or choose existing one from dropdown
* Import actions through **Import** button
  * Currently only file imports are supported
* Apply actions through **Apply** button
* Export, if you want