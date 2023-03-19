# Animation Combiner for Blender
[![Latest Release](https://img.shields.io/github/v/release/pehala/AnimationCombiner)](https://github.com/pehala/animationCombiner/releases/latest)
[![License](https://img.shields.io/github/license/pehala/animationCombiner)](https://github.com/pehala/animationCombiner/blob/main/LICENSE)


This is a plugin for [Blender](https://www.blender.org/) (3.0+), which simplifies creating animation by combining simple ones through custom UI.

## Current capabilities
* Can import/export animation from [MESSIF](https://gitlab.fi.muni.cz/disa/public/messif) .data files (if you would like to add more formats, please create an issue)
* Combines multiple animation into one
* Ability to apply animations only to a specific body parts
* Can interpolate between different animations

## Limitations
* Only one format supported so far
* All animation needs to have same framerate
   * Not 100% true, you can slow down individual animation, however working with different framerates is cumbersome  

## Planned features
* More formats!
* More skeleton types and ability to interpolate between them
* Ability to work with multiple frame rates and export to a specific one

## Installation
* [Download the latest archive from releases](https://github.com/pehala/animationCombiner/releases/latest)
* Install plugin to Blender
  * **Edit** -> **Preferences** -> **Install**..
  * Search for "**Animation Combiner**"
  * Enable plugin


## Basic idea
* In this plugin the individual animations, called **Actions**, are group together in **Groups** and are applied at the same time, **Groups** are applied in sequentially in the specific order. Each **Action** has a number of settings like _slowdown_, _transition_  which are used to configure how precisely the **Action** is blended with other **Actions**. You can also select to which body parts the Action applies, however only one **Action** can be applied to every single body part in the **Group**

## Usage
* Look into the right side of the viewport and switch to Animation tab
  * All UI elements are under one panel called **AnimationCombiner**
* Create new armature through **Create Armature** button or choose existing one from dropdown
* Create new group 
* Import actions into that group
  * Currently only file imports are supported
* Apply actions through **Apply** button
* Export, if you want