/****** Object:  Table [dbo].[WeatherCache]    Script Date: 10.08.2021 16:44:22 ******/

SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

IF NOT EXISTS (SELECT * 
FROM sysobjects 
WHERE name='WeatherCache')

CREATE TABLE [dbo].[WeatherCache](
	[ID] [uniqueidentifier] NOT NULL,
	[CityTitle] [varchar](255) NULL,
	[WoeID] [int] NOT NULL,
	[Date] [date] NOT NULL,
	[MaxTemp] [smallint] NOT NULL,
	[MinTemp] [smallint] NOT NULL,
	[Humidity] [tinyint] NOT NULL,
 CONSTRAINT [PK_WeatherCache] PRIMARY KEY CLUSTERED 
(
	[ID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY],
 CONSTRAINT [UC_Date] UNIQUE NONCLUSTERED 
(
	[WoeID] ASC,
	[Date] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO

GO

ALTER TABLE [dbo].[WeatherCache] ADD  CONSTRAINT [DF_WeatherCache_ID]  DEFAULT (newid()) FOR [ID]
GO

ALTER TABLE [dbo].[WeatherCache] ADD  CONSTRAINT [DF_WeatherCache_CityTitle]  DEFAULT ('St Petersburg') FOR [CityTitle]
GO

ALTER TABLE [dbo].[WeatherCache] ADD  CONSTRAINT [DF_WeatherCache_WoeID]  DEFAULT ((2123260)) FOR [WoeID]
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'St Petersburg by default' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'WeatherCache', @level2type=N'COLUMN',@level2name=N'CityTitle'
GO

EXEC sys.sp_addextendedproperty @name=N'MS_Description', @value=N'St Petersburg woeid by default' , @level0type=N'SCHEMA',@level0name=N'dbo', @level1type=N'TABLE',@level1name=N'WeatherCache', @level2type=N'COLUMN',@level2name=N'WoeID'
GO
