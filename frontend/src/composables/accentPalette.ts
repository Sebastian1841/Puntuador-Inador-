// Choose readable text even for very light or very dark custom accents.
export function accentPalette(value: string) {
  const accent = /^#[0-9a-f]{6}$/i.test(value) ? value : '#008cff'
  const channels = [1, 3, 5].map(i => {
    const channel = parseInt(accent.slice(i, i + 2), 16) / 255
    return channel <= .04045 ? channel / 12.92 : ((channel + .055) / 1.055) ** 2.4
  })
  const luminance = channels[0]! * .2126 + channels[1]! * .7152 + channels[2]! * .0722
  return { '--accent': accent, '--on-accent': luminance > .179 ? '#000000' : '#ffffff' }
}
