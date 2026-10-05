import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "Robótica Móvil",
  description: "Memoria de prácticas de Unibotics",
  // ESTA LÍNEA ES OBLIGATORIA PARA TU GITHUB:
  base: '/ROBOTICAMOVILPRACT/',

  themeConfig: {
    nav: [
      { text: 'Inicio', link: '/' },
      { text: 'Prácticas', link: '/practica-1' }
    ],

    sidebar: [
      {
        text: 'Memorias del Curso',
        items: [
          { text: 'Práctica 1: Aspirador autónomo', link: '/practica-1' },
          { text: 'Práctica 2: Sigue-líneas', link: '/practica-2' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/JaviSVJ/ROBOTICAMOVILPRACT' }
    ]
  }
})